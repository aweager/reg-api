from dataclasses import dataclass, field
from enum import StrEnum

from dataclasses_json import config
from jrpc.data import JsonTryLoadMixin
from jrpc.service import JsonTryConverter, MethodDescriptor
from marshmallow import fields
from result import Err, Ok, Result

from .errors import ERROR_CONVERTER


# fmt: off
class Regname(StrEnum):
    unnamed = "unnamed"
    a = "a"; b = "b"; c = "c"; d = "d"; e = "e"; f = "f"
    g = "g"; h = "h"; i = "i"; j = "j"; k = "k"; l = "l"
    m = "m"; n = "n"; o = "o"; p = "p"; q = "q"; r = "r"
    s = "s"; t = "t"; u = "u"; v = "v"; w = "w"; x = "x"
    y = "y"; z = "z"
# fmt: on


def parse_regname(register: str) -> Result[Regname, str]:
    if register in Regname.__members__:
        return Ok(Regname.__members__[register])
    return Err("Register name must be 'unnamed' or a-z")


def keys_field():
    return field(metadata=config(mm_field=fields.List(fields.Enum(Regname, by_value=True))))


def values_field(allow_none: bool):
    return field(
        metadata=config(
            mm_field=fields.Mapping(
                keys=fields.Enum(Regname, by_value=True), values=fields.Str(allow_none=allow_none)
            )
        )
    )


@dataclass
class RegistryInfoParams(JsonTryLoadMixin):
    registry: str


@dataclass
class RegistryInfoResult(JsonTryLoadMixin):
    exists: bool


@dataclass
class GetMultipleParams(JsonTryLoadMixin):
    registry: str
    keys: list[Regname] = keys_field()


@dataclass
class GetMultipleResult(JsonTryLoadMixin):
    values: dict[Regname, str | None] = values_field(allow_none=True)


@dataclass
class GetAllParams(JsonTryLoadMixin):
    registry: str


@dataclass
class GetAllResult(JsonTryLoadMixin):
    values: dict[Regname, str] = values_field(allow_none=False)


@dataclass
class SetMultipleParams(JsonTryLoadMixin):
    registry: str
    values: dict[Regname, str | None] = values_field(allow_none=True)


@dataclass
class SetMultipleResult(JsonTryLoadMixin):
    pass


@dataclass
class ClearAndReplaceParams(JsonTryLoadMixin):
    registry: str
    values: dict[Regname, str] = values_field(allow_none=False)


@dataclass
class ClearAndReplaceResult(JsonTryLoadMixin):
    pass


@dataclass
class RegLink(JsonTryLoadMixin):
    instance: str
    registry: str


@dataclass
class AddLinkParams(JsonTryLoadMixin):
    registry: str
    link: RegLink


@dataclass
class AddLinkResult(JsonTryLoadMixin):
    pass


@dataclass
class RemoveLinkParams(JsonTryLoadMixin):
    registry: str
    link: RegLink


@dataclass
class RemoveLinkResult(JsonTryLoadMixin):
    pass


@dataclass
class SyncMultipleParams(JsonTryLoadMixin):
    source_link: RegLink
    visited_registries: list[RegLink]
    registry: str
    values: dict[Regname, str | None] = values_field(allow_none=True)


@dataclass
class SyncAcceptance(JsonTryLoadMixin):
    link: RegLink
    accepted: bool


@dataclass
class SyncMultipleResult(JsonTryLoadMixin):
    sync_acceptance: list[SyncAcceptance]


@dataclass
class SyncAllParams(JsonTryLoadMixin):
    source_link: RegLink
    visited_registries: list[RegLink]
    registry: str
    values: dict[Regname, str] = values_field(allow_none=False)


@dataclass
class SyncAllResult(JsonTryLoadMixin):
    sync_acceptance: list[SyncAcceptance]


class RegMethod:
    REGISTRY_INFO = MethodDescriptor(
        name="reg.registry-info",
        params_converter=JsonTryConverter(RegistryInfoParams),
        result_converter=JsonTryConverter(RegistryInfoResult),
        error_converter=ERROR_CONVERTER,
    )

    GET_MULTIPLE = MethodDescriptor(
        name="reg.get-multiple",
        params_converter=JsonTryConverter(GetMultipleParams),
        result_converter=JsonTryConverter(GetMultipleResult),
        error_converter=ERROR_CONVERTER,
    )
    GET_ALL = MethodDescriptor(
        name="reg.get-all",
        params_converter=JsonTryConverter(GetAllParams),
        result_converter=JsonTryConverter(GetAllResult),
        error_converter=ERROR_CONVERTER,
    )

    SET_MULTIPLE = MethodDescriptor(
        name="reg.set-multiple",
        params_converter=JsonTryConverter(SetMultipleParams),
        result_converter=JsonTryConverter(SetMultipleResult),
        error_converter=ERROR_CONVERTER,
    )
    CLEAR_AND_REPLACE = MethodDescriptor(
        name="reg.clear-and-replace",
        params_converter=JsonTryConverter(ClearAndReplaceParams),
        result_converter=JsonTryConverter(ClearAndReplaceResult),
        error_converter=ERROR_CONVERTER,
    )

    ADD_LINK = MethodDescriptor(
        name="reg.add-link",
        params_converter=JsonTryConverter(AddLinkParams),
        result_converter=JsonTryConverter(AddLinkResult),
        error_converter=ERROR_CONVERTER,
    )
    REMOVE_LINK = MethodDescriptor(
        name="reg.remove-link",
        params_converter=JsonTryConverter(RemoveLinkParams),
        result_converter=JsonTryConverter(RemoveLinkResult),
        error_converter=ERROR_CONVERTER,
    )

    SYNC_MULTIPLE = MethodDescriptor(
        name="reg.sync-multiple",
        params_converter=JsonTryConverter(SyncMultipleParams),
        result_converter=JsonTryConverter(SyncMultipleResult),
        error_converter=ERROR_CONVERTER,
    )
    SYNC_ALL = MethodDescriptor(
        name="reg.sync-all",
        params_converter=JsonTryConverter(SyncAllParams),
        result_converter=JsonTryConverter(SyncAllResult),
        error_converter=ERROR_CONVERTER,
    )
