from jrpc.service import JsonRpcProcessor, MethodSet, TypedMethodHandler

from .api import RegMethod
from .service import RegApi


def reg_rpc_processor(impl: RegApi) -> JsonRpcProcessor:
    handlers: list[TypedMethodHandler] = [
        TypedMethodHandler(RegMethod.REGISTRY_INFO, impl.get_registry_info),
        TypedMethodHandler(RegMethod.GET_MULTIPLE, impl.get_multiple),
        TypedMethodHandler(RegMethod.GET_ALL, impl.get_all),
        TypedMethodHandler(RegMethod.SET_MULTIPLE, impl.set_multiple),
        TypedMethodHandler(RegMethod.CLEAR_AND_REPLACE, impl.clear_and_replace),
        TypedMethodHandler(RegMethod.ADD_LINK, impl.add_link),
        TypedMethodHandler(RegMethod.REMOVE_LINK, impl.remove_link),
        TypedMethodHandler(RegMethod.SYNC_MULTIPLE, impl.sync_multiple),
        TypedMethodHandler(RegMethod.SYNC_ALL, impl.sync_all),
    ]
    return MethodSet({m.descriptor.name: m for m in handlers})
