from abc import ABC, abstractmethod

from result import Result

from reg.api import (
    AddLinkParams,
    AddLinkResult,
    ListLinksParams,
    ListLinksResult,
    RemoveLinkParams,
    RemoveLinkResult,
    SyncAllParams,
    SyncAllResult,
    SyncMultipleParams,
    SyncMultipleResult,
)

from .api import (
    ClearAndReplaceParams,
    ClearAndReplaceResult,
    GetAllParams,
    GetAllResult,
    GetMultipleParams,
    GetMultipleResult,
    RegistryInfoParams,
    RegistryInfoResult,
    SetMultipleParams,
    SetMultipleResult,
)
from .errors import RegApiError


class RegApiImpl(ABC):
    @abstractmethod
    async def get_registry_info(
        self, params: RegistryInfoParams
    ) -> Result[RegistryInfoResult, RegApiError]:
        pass

    @abstractmethod
    async def get_multiple(
        self, params: GetMultipleParams
    ) -> Result[GetMultipleResult, RegApiError]:
        pass

    @abstractmethod
    async def get_all(self, params: GetAllParams) -> Result[GetAllResult, RegApiError]:
        pass

    @abstractmethod
    async def set_multiple(
        self, params: SetMultipleParams
    ) -> Result[SetMultipleResult, RegApiError]:
        pass

    @abstractmethod
    async def clear_and_replace(
        self, params: ClearAndReplaceParams
    ) -> Result[ClearAndReplaceResult, RegApiError]:
        pass

    @abstractmethod
    async def list_links(self, params: ListLinksParams) -> Result[ListLinksResult, RegApiError]:
        pass

    @abstractmethod
    async def add_link(self, params: AddLinkParams) -> Result[AddLinkResult, RegApiError]:
        pass

    @abstractmethod
    async def remove_link(self, params: RemoveLinkParams) -> Result[RemoveLinkResult, RegApiError]:
        pass

    @abstractmethod
    async def sync_multiple(
        self, params: SyncMultipleParams
    ) -> Result[SyncMultipleResult, RegApiError]:
        pass

    @abstractmethod
    async def sync_all(self, params: SyncAllParams) -> Result[SyncAllResult, RegApiError]:
        pass
