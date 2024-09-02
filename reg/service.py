from abc import ABC, abstractmethod

from jrpc.service import MethodSet, implements, make_method_set
from result import Result

from .api import (
    AddLinkParams,
    AddLinkResult,
    ClearAndReplaceParams,
    ClearAndReplaceResult,
    GetAllParams,
    GetAllResult,
    GetMultipleParams,
    GetMultipleResult,
    RegistryInfoParams,
    RegistryInfoResult,
    RegMethod,
    RemoveLinkParams,
    RemoveLinkResult,
    SetMultipleParams,
    SetMultipleResult,
    SyncAllParams,
    SyncAllResult,
    SyncMultipleParams,
    SyncMultipleResult,
)
from .errors import RegApiError


class RegApi(ABC):
    @implements(RegMethod.REGISTRY_INFO)
    @abstractmethod
    async def get_registry_info(
        self, params: RegistryInfoParams
    ) -> Result[RegistryInfoResult, RegApiError]:
        pass

    @implements(RegMethod.GET_MULTIPLE)
    @abstractmethod
    async def get_multiple(
        self, params: GetMultipleParams
    ) -> Result[GetMultipleResult, RegApiError]:
        pass

    @implements(RegMethod.GET_ALL)
    @abstractmethod
    async def get_all(self, params: GetAllParams) -> Result[GetAllResult, RegApiError]:
        pass

    @implements(RegMethod.SET_MULTIPLE)
    @abstractmethod
    async def set_multiple(
        self, params: SetMultipleParams
    ) -> Result[SetMultipleResult, RegApiError]:
        pass

    @implements(RegMethod.CLEAR_AND_REPLACE)
    @abstractmethod
    async def clear_and_replace(
        self, params: ClearAndReplaceParams
    ) -> Result[ClearAndReplaceResult, RegApiError]:
        pass

    @implements(RegMethod.ADD_LINK)
    @abstractmethod
    async def add_link(self, params: AddLinkParams) -> Result[AddLinkResult, RegApiError]:
        pass

    @implements(RegMethod.REMOVE_LINK)
    @abstractmethod
    async def remove_link(self, params: RemoveLinkParams) -> Result[RemoveLinkResult, RegApiError]:
        pass

    @implements(RegMethod.SYNC_MULTIPLE)
    @abstractmethod
    async def sync_multiple(
        self, params: SyncMultipleParams
    ) -> Result[SyncMultipleResult, RegApiError]:
        pass

    @implements(RegMethod.SYNC_ALL)
    @abstractmethod
    async def sync_all(self, params: SyncAllParams) -> Result[SyncAllResult, RegApiError]:
        pass

    def method_set(self) -> MethodSet:
        return make_method_set(RegApi, self)
