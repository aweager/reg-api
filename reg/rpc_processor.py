from dataclasses import dataclass
from typing import TypeVar, assert_never

from dataclasses_json import DataClassJsonMixin
from jrpc.data import JsonRpcError, JsonRpcParams, ParsedJson
from jrpc.errors import invalid_params, method_not_found
from result import Err, Ok, Result

from .api import (
    AddLinkParams,
    ClearAndReplaceParams,
    GetAllParams,
    GetMultipleParams,
    JsonTryLoadMixin,
    ListLinksParams,
    RegistryInfoParams,
    RegMethodName,
    RemoveLinkParams,
    SetMultipleParams,
    SyncAllParams,
    SyncMultipleParams,
    SyncMultipleResult,
)
from .errors import RegApiError
from .model import RegApiImpl

_methods: dict[str, type[JsonTryLoadMixin]] = {
    RegMethodName.REGISTRY_INFO: RegistryInfoParams,
    RegMethodName.GET_MULTIPLE: GetMultipleParams,
    RegMethodName.GET_ALL: GetAllParams,
    RegMethodName.SET_MULTIPLE: SetMultipleParams,
    RegMethodName.CLEAR_AND_REPLACE: ClearAndReplaceParams,
    RegMethodName.LIST_LINKS: ListLinksParams,
    RegMethodName.ADD_LINK: AddLinkParams,
    RegMethodName.REMOVE_LINK: RemoveLinkParams,
    RegMethodName.SYNC_MULTIPLE: SyncMultipleParams,
    RegMethodName.SYNC_ALL: SyncAllParams,
}


@dataclass
class RegRpcProcessor:
    model: RegApiImpl

    async def __call__(
        self, method: str, params: JsonRpcParams
    ) -> Result[ParsedJson, JsonRpcError]:
        if not method in _methods:
            return Err(method_not_found(method))

        params_type = _methods[method]
        match params_type.try_load(params):
            case Ok(loaded_params):
                result = await self._process_params(loaded_params)
                return result.map(DataClassJsonMixin.to_dict).map_err(RegApiError.to_json_rpc_error)
            case Err(schema_error):
                return Err(invalid_params(schema_error))

    async def _process_params(self, params) -> Result[DataClassJsonMixin, RegApiError]:
        match params:
            case RegistryInfoParams():
                return await self.model.get_registry_info(params)
            case GetMultipleParams():
                return await self.model.get_multiple(params)
            case GetAllParams():
                return await self.model.get_all(params)
            case SetMultipleParams():
                return await self.model.set_multiple(params)
            case ClearAndReplaceParams():
                return await self.model.clear_and_replace(params)
            case ListLinksParams():
                return await self.model.list_links(params)
            case AddLinkParams():
                return await self.model.add_link(params)
            case RemoveLinkParams():
                return await self.model.remove_link(params)
            case SyncMultipleParams():
                return await self.model.sync_multiple(params)
            case SyncAllParams():
                return await self.model.sync_all(params)
            case _:
                assert_never(params)
