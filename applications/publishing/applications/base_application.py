from typing import Any, ClassVar

from django.db.models import QuerySet
from django.db.transaction import atomic
from rest_framework import exceptions

from applications.common.utils import get_dataclass_fields
from applications.common.event_source.event_store import EventStore
from applications.publishing.typing import RawData, DataclassProtocol


class BaseApplicationMixin:
    event_store: EventStore
    aggregate_class: ClassVar = None

    def _check_edit_action(self, raw_data: RawData):
        if not raw_data.get("aggregate_id"):
            msg = "This action Required an instance identifier."
            raise exceptions.ValidationError(msg)

    def reconstruct_state(self, aggregate_id: str):
        event_stream = self.event_store.load_stream(aggregate_id)
        aggregate: Any = None
        for index, db_event in enumerate(event_stream.events):
            if index == 0:
                raw_data = dict(event_type=db_event.event_type, data=db_event.data)
                aggregate = self.aggregate_class(raw_data)
                continue
            event_ = aggregate.process_event(raw_data=db_event.to_raw_data())
            aggregate.apply(event_)
        aggregate.version = event_stream.version
        return aggregate

    def _edit_type_save(self, raw_data: RawData):  # ToDo edit aggregate model should be handled by aggregate class
        self._check_edit_action(raw_data)
        aggregate: Any = self.reconstruct_state(raw_data['aggregate_id'])
        if aggregate:
            expected_version = aggregate.version
            aggregate.apply(self._create_event_dataclass(raw_data))
            self.event_store.append_to_stream(
                aggregate_uuid=raw_data['aggregate_id'],
                event=aggregate.last_event,
                expected_version=expected_version
            )

    @classmethod
    def _create_event_dataclass(cls, raw_data: RawData) -> DataclassProtocol:
        event_dataclass_obj = cls.aggregate_class.process_event(raw_data)
        return event_dataclass_obj

    @staticmethod
    def __get_dataclass_fields(dataclass) -> list:
        return get_dataclass_fields(dataclass)


class EventsApplication(BaseApplicationMixin):
    aggregate_class: ClassVar = None
    aggregate_store_model: ClassVar = None
    event_store_model: ClassVar = None

    def __init__(self) -> None:
        self.event_store = EventStore(self.aggregate_store_model, self.event_store_model)

    @atomic
    def create(self, raw_data: RawData):
        post = self.aggregate_class(raw_data)
        aggregate = self.event_store.create_aggregate(post)
        self.event_store.append_to_stream(
            aggregate_uuid=aggregate.id,
            event=post.last_event,
        )
        return aggregate

    @atomic
    def edit(self, raw_data: RawData):
        self._edit_type_save(raw_data)

    def retrieve(self, aggregate_id: str):
        return self.event_store.get_aggregate(aggregate_id)

    def retrieve_by_reconstructing(self, aggregate_id: str):
        return self.event_store.load_stream(aggregate_id)  # FixMe

    def list(self) -> QuerySet:
        return self.event_store.get_aggregate_list()

    def retrieve_aggregate_events(self, aggregate_id: str) -> list:
        aggregate = self.reconstruct_state(aggregate_id)
        return aggregate.collect_events()
