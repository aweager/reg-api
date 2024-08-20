from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypeVar, override

from jrpc import client as jrpc_client
from jrpc.data import JsonRpcError, JsonTryLoadMixin, ParsedJson
from result import Err, Ok, Result

from .errors import RegApiError, ResponseSchemaMismatch


class RegMethodName(StrEnum):
    REGISTRY_INFO = "reg.registry-info"

    GET_MULTIPLE = "reg.get-multiple"
    GET_ALL = "reg.get-all"

    SET_MULTIPLE = "reg.set-multiple"
    CLEAR_AND_REPLACE = "reg.clear-and-replace"

    LIST_LINKS = "reg.list-links"
    ADD_LINK = "reg.add-link"
    REMOVE_LINK = "reg.remove-link"

    SYNC_MULTIPLE = "reg.sync-multiple"
    SYNC_ALL = "reg.sync-all"


_TParams = TypeVar("_TParams", bound=JsonTryLoadMixin)
_TResult = TypeVar("_TResult", bound=JsonTryLoadMixin)


class _RegRequestDefinition(
    Generic[_TParams, _TResult], jrpc_client.RequestDefinition[_TResult, RegApiError]
):
    _result_type: type[_TResult]

    def __init__(
        self, method: RegMethodName, params: _TParams, result_type: type[_TResult]
    ) -> None:
        super().__init__(method.value, params.to_dict())
        self._result_type = result_type

    @override
    def load_result(self, result: ParsedJson) -> Result[_TResult, RegApiError]:
        match self._result_type.try_load(result):
            case Ok() as ok:
                return ok
            case Err(msg):
                return Err(
                    RegApiError.from_data(ResponseSchemaMismatch(self._result_type.__name__, msg))
                )

    @override
    def convert_error(self, error: JsonRpcError) -> RegApiError:
        return RegApiError.from_json_rpc_error(error)


@dataclass
class RegistryInfoParams(JsonTryLoadMixin):
    ref: str


@dataclass
class RegistryInfoResult(JsonTryLoadMixin):
    exists: bool
    id: str | None


class RegistryInfo(_RegRequestDefinition[RegistryInfoParams, RegistryInfoResult]):
    def __init__(self, params: RegistryInfoParams) -> None:
        super().__init__(RegMethodName.REGISTRY_INFO, params, RegistryInfoResult)


@dataclass
class GetMultipleParams(JsonTryLoadMixin):
    location: str
    namespace: str
    keys: list[str]


@dataclass
class GetMultipleResult(JsonTryLoadMixin):
    values: dict[str, str | None]


class GetMultiple(_RegRequestDefinition[GetMultipleParams, GetMultipleResult]):
    def __init__(self, params: GetMultipleParams) -> None:
        super().__init__(RegMethodName.GET_MULTIPLE, params, GetMultipleResult)


@dataclass
class GetAllParams(JsonTryLoadMixin):
    location: str
    namespace: str


@dataclass
class GetAllResult(JsonTryLoadMixin):
    values: dict[str, str]


class GetAll(_RegRequestDefinition[GetAllParams, GetAllResult]):
    def __init__(self, params: GetAllParams) -> None:
        super().__init__(
            RegMethodName.GET_ALL,
            params,
            GetAllResult,
        )


@dataclass
class SetMultipleParams(JsonTryLoadMixin):
    location: str
    namespace: str
    values: dict[str, str | None]


@dataclass
class SetMultipleResult(JsonTryLoadMixin):
    pass


class SetMultiple(_RegRequestDefinition[SetMultipleParams, SetMultipleResult]):
    def __init__(self, params: SetMultipleParams) -> None:
        super().__init__(RegMethodName.SET_MULTIPLE, params, SetMultipleResult)


@dataclass
class ClearAndReplaceParams(JsonTryLoadMixin):
    location: str
    namespace: str
    values: dict[str, str]


@dataclass
class ClearAndReplaceResult(JsonTryLoadMixin):
    pass


class ClearAndReplace(_RegRequestDefinition[ClearAndReplaceParams, ClearAndReplaceResult]):
    def __init__(self, params: ClearAndReplaceParams) -> None:
        super().__init__(RegMethodName.CLEAR_AND_REPLACE, params, ClearAndReplaceResult)


@dataclass
class ListLinksParams(JsonTryLoadMixin):
    registry: str


@dataclass
class ListLinksResult(JsonTryLoadMixin):
    pass


class ListLinks(_RegRequestDefinition[ListLinksParams, ListLinksResult]):
    def __init__(self, params: ListLinksParams) -> None:
        super().__init__(RegMethodName.LIST_LINKS, params, ListLinksResult)


@dataclass
class AddLinkParams(JsonTryLoadMixin):
    pass


@dataclass
class AddLinkResult(JsonTryLoadMixin):
    pass


class AddLink(_RegRequestDefinition[AddLinkParams, AddLinkResult]):
    def __init__(self, params: AddLinkParams) -> None:
        super().__init__(RegMethodName.ADD_LINK, params, AddLinkResult)


@dataclass
class RemoveLinkParams(JsonTryLoadMixin):
    pass


@dataclass
class RemoveLinkResult(JsonTryLoadMixin):
    pass


class RemoveLink(_RegRequestDefinition[RemoveLinkParams, RemoveLinkResult]):
    def __init__(self, params: RemoveLinkParams) -> None:
        super().__init__(RegMethodName.REMOVE_LINK, params, RemoveLinkResult)


@dataclass
class SyncMultipleParams(JsonTryLoadMixin):
    pass


@dataclass
class SyncMultipleResult(JsonTryLoadMixin):
    pass


class SyncMultiple(_RegRequestDefinition[SyncMultipleParams, SyncMultipleResult]):
    def __init__(self, params: SyncMultipleParams) -> None:
        super().__init__(RegMethodName.SYNC_MULTIPLE, params, SyncMultipleResult)


@dataclass
class SyncAllParams(JsonTryLoadMixin):
    pass


@dataclass
class SyncAllResult(JsonTryLoadMixin):
    pass


class SyncAll(_RegRequestDefinition[SyncAllParams, SyncAllResult]):
    def __init__(self, params: SyncAllParams) -> None:
        super().__init__(RegMethodName.SYNC_ALL, params, SyncAllResult)
