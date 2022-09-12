import abc
import dataclasses
import typing
import uuid

from django.db.models import QuerySet
from django.db.transaction import atomic
from rest_framework import exceptions

from applications.common.models.event_source import EventModel
from applications.common.utils import get_object_or_none


@dataclasses.dataclass
class EventStream:
    events: list[EventModel]
    version: int
    aggregate: typing.Any


class IEventStore(abc.ABC):

    @abc.abstractmethod
    def load_stream(self, aggregate_uuid: uuid.UUID) -> EventStream:
        raise NotImplementedError

    @abc.abstractmethod
    def append_to_stream(
            self,
            aggregate_uuid: uuid.UUID,
            expected_version: typing.Optional[int],
            events: typing.List[EventModel]
    ) -> None:
        raise NotImplementedError


class AggregateType(typing.Protocol):
    title: str
    content: str
    slug: str
    status: int
    creator_id: int
    action_by: int

    as_dict: dict

    @abc.abstractmethod
    def as_dict(self):
        raise NotImplementedError


class EventStore(IEventStore):
    aggregate_store_model: typing.Any
    event_store_model: typing.Any

    def __init__(self, aggregate_model, event_model) -> None:
        self.aggregate_store_model = aggregate_model
        self.event_store_model = event_model

    @property
    def aggregate_model(self):
        if self.aggregate_store_model is None:
            msg = "Implement aggregate_store_model"
            raise NotImplementedError(msg)
        return self.aggregate_store_model

    @property
    def event_model(self):
        if self.event_store_model is None:
            msg = "Implement event_store_model"
            raise NotImplementedError(msg)
        return self.event_store_model

    def load_stream(self, aggregate_uuid: str) -> EventStream:
        aggregate = self.aggregate_model.objects.get(id=aggregate_uuid)

        return EventStream(aggregate.events.all(), aggregate.version, aggregate=aggregate)

    def get_aggregate_list(self) -> QuerySet:
        return self.aggregate_store_model.objects.all()

    @atomic
    def append_to_stream(
            self,
            aggregate_uuid: str,
            event: dataclasses.dataclass,
            aggregate_data: dict,
            expected_version: int = None
    ):
        if expected_version:  # update
            row_count = (
                self.aggregate_model.objects
                .filter(id=aggregate_uuid, version=expected_version)
                .update(version=expected_version + 1, **aggregate_data)
            )
            if row_count != 1:  # should be one
                msg = "Concurrent Race condition error. Retry!"
                raise exceptions.ValidationError(msg)

        self.event_store_model.objects.create(
            aggregate_id=str(aggregate_uuid),
            event_type=str(event),
            data=dataclasses.asdict(event)
        )

    def create_aggregate(self, aggregate: AggregateType):
        data = {key: value for key, value in aggregate.as_dict.items() if value}
        return self.aggregate_store_model.objects.create(**data)

    def get_aggregate(self, aggregate_id: str):
        return get_object_or_none(self.aggregate_model, id=aggregate_id)

    def update_aggregate(self, aggregate: AggregateType, aggregate_id: str):
        return (
            self.aggregate_store_model.objects
            .filter(aggregate_id=aggregate_id)
            .update(**aggregate.as_dict())
        )
