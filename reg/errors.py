from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Any, Callable, Mapping, TypeVar

from dataclasses_json import DataClassJsonMixin
from dataclasses_json.mm import SchemaType
from jrpc.data import JsonRpcError, ParsedJson


class RegErrorCode(Enum):
    REGISTRY_DOES_NOT_EXIST = 11003
    RESPONSE_SCHEMA_MISMATCH = 11004


_registry_by_code: dict[int, Callable[[ParsedJson], Any]] = {}
_registry_by_type: dict[type[DataClassJsonMixin], tuple[int, str]] = {}

_T = TypeVar("_T")


def _load_if_dict(schema: SchemaType[_T], parsed_json: ParsedJson) -> _T | None:
    if not isinstance(parsed_json, Mapping):
        return None
    if not isinstance(parsed_json, dict):
        parsed_json = dict(parsed_json)

    try:
        return schema.load(parsed_json, unknown="exclude")
    except ValueError:
        # Swallow error load issues
        return None


def register_error_type(
    code: int, message: str, data_type: type[DataClassJsonMixin]
) -> None:
    _registry_by_code[code] = partial(_load_if_dict, data_type.schema())
    _registry_by_type[data_type] = (code, message)


@dataclass
class RegApiError:
    code: int
    message: str
    raw_data: ParsedJson

    def __post_init__(self) -> None:
        if self.code in _registry_by_code:
            self.data = _registry_by_code[self.code](self.raw_data)
        else:
            self.data = None

    def to_json_rpc_error(self) -> JsonRpcError:
        return JsonRpcError(self.code, self.message, self.raw_data)

    @staticmethod
    def from_json_rpc_error(error: JsonRpcError) -> "RegApiError":
        return RegApiError(error.code, error.message, error.data)

    @staticmethod
    def from_data(data: DataClassJsonMixin) -> "RegApiError":
        if type(data) not in _registry_by_type:
            raise ValueError()
        code, message = _registry_by_type[type(data)]
        return RegApiError(code, message, data.to_dict())


@dataclass
class RegistryDoesNotExist(DataClassJsonMixin):
    reference: str


register_error_type(
    code=RegErrorCode.REGISTRY_DOES_NOT_EXIST.value,
    message="Registry does not exist",
    data_type=RegistryDoesNotExist,
)


@dataclass
class ResponseSchemaMismatch(DataClassJsonMixin):
    schema_name: str
    details: str


register_error_type(
    code=RegErrorCode.RESPONSE_SCHEMA_MISMATCH.value,
    message="Response schema does not match",
    data_type=ResponseSchemaMismatch,
)
