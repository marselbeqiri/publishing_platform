import dataclasses
from abc import ABC, abstractmethod
from typing import ClassVar, Type

from rest_framework import serializers

from applications.publishing.typing import RawData, DataclassProtocol


class EventSerializer(serializers.Serializer):
    event_class = None

    def init_event(self):
        if self.event_class is None:
            msg = "Implement event_class of dataclass type"
            raise NotImplementedError(msg)
        self.is_valid(raise_exception=True)

        return self.event_class(**self.data)


class AggregateBase(ABC):
    _EVENT_MAP: ClassVar[dict[str, Type[EventSerializer]]] = None
    _events: list

    def __init__(self, event: RawData):
        self._events = []
        self.apply(
            self.process_event(event)
        )

    @classmethod
    def process_event(cls, raw_data: RawData) -> DataclassProtocol:
        event_type: str = str(raw_data['event_type'])
        data: dict = raw_data['data']

        return cls._EVENT_MAP[event_type](data=data).init_event()

    @classmethod
    def get_event_class(cls, event_type: str) -> Type[DataclassProtocol]:
        return cls._EVENT_MAP[event_type].event_class

    def collect_events(self):
        return self._events

    @property
    def last_event(self):
        return self._events[-1]

    def apply(self, event: dataclasses.dataclass):
        self._apply(event)
        self._events.append(event)

    @abstractmethod
    def _apply(self, event):
        raise NotImplementedError

    @abstractmethod
    def as_dict(self):
        raise NotImplementedError
