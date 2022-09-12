from typing import TypedDict, Protocol, Optional, Callable


class RawData(TypedDict):
    data: dict
    aggregate_id: str
    event_type: str


class DataclassProtocol(Protocol):
    __dataclass_fields__: dict
    __dataclass_params__: dict
    __post_init__: Optional[Callable]
