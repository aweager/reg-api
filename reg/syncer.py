import asyncio
import itertools
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import partial

from jrpc.client import ClientManager

from .api import (
    RegLink,
    RegMethod,
    Regname,
    SyncAcceptance,
    SyncAllParams,
    SyncAllResult,
    SyncMultipleParams,
    SyncMultipleResult,
)

_SyncMethod = Callable[[RegLink, list[RegLink], RegLink], Awaitable[list[SyncAcceptance]]]

_LOGGER = logging.getLogger("reg-syncer")


@dataclass
class RegSyncer:
    clients: ClientManager
    this_instance: str

    async def forward_sync_multiple(
        self,
        registry: str,
        visited_registries: list[RegLink],
        values: dict[Regname, str | None],
        links: list[RegLink],
    ) -> SyncMultipleResult:
        return SyncMultipleResult(
            await self._forward_sync(
                this_registry=registry,
                visited_registries=visited_registries,
                sync_method=partial(self._call_sync_multiple, values=values),
                links=links,
            )
        )

    async def forward_sync_all(
        self,
        registry: str,
        visited_registries: list[RegLink],
        values: dict[Regname, str],
        links: list[RegLink],
    ) -> SyncAllResult:
        return SyncAllResult(
            await self._forward_sync(
                this_registry=registry,
                visited_registries=visited_registries,
                sync_method=partial(self._call_sync_all, values=values),
                links=links,
            )
        )

    async def _forward_sync(
        self,
        visited_registries: list[RegLink],
        this_registry: str,
        sync_method: _SyncMethod,
        links: list[RegLink],
    ) -> list[SyncAcceptance]:
        this_link = RegLink(self.this_instance, this_registry)
        visited_registries.append(this_link)
        unvisited_links = [link for link in links if link not in visited_registries]

        _LOGGER.info(f"Syncing...")
        _LOGGER.info(f"    links = {links}")
        _LOGGER.info(f"    visited_registries = {visited_registries}")
        _LOGGER.info(f"    unvisited_links = {unvisited_links}")

        visited_registries.extend(links)
        deduplicated: list[RegLink] = []
        for link in visited_registries:
            if link not in deduplicated:
                deduplicated.append(link)
        visited_registries = deduplicated

        _LOGGER.info(f"    deduplicated = {visited_registries}")

        acceptance_list = [
            a
            for result in await asyncio.gather(
                *[sync_method(this_link, visited_registries, link) for link in unvisited_links]
            )
            for a in result
        ]
        acceptance_list.append(SyncAcceptance(this_link, True))

        acceptance_dict: dict[tuple[str, str], SyncAcceptance] = {}
        for acc_key, acc_copies in itertools.groupby(
            acceptance_list,
            lambda a: (a.link.instance, a.link.registry),
        ):
            is_accepted = False
            for acceptance in acc_copies:
                if acceptance.accepted:
                    is_accepted = True
                    break
            acceptance_dict[acc_key] = SyncAcceptance(RegLink(acc_key[0], acc_key[1]), is_accepted)

        _LOGGER.info(f"    acceptance: {acceptance_dict}")
        return list(acceptance_dict.values())

    async def _call_sync_multiple(
        self,
        this_link: RegLink,
        visited_registries: list[RegLink],
        to_link: RegLink,
        values: dict[Regname, str | None],
    ) -> list[SyncAcceptance]:
        async with self.clients.client(to_link.instance) as client:
            return (
                (
                    await client.request(
                        descriptor=RegMethod.SYNC_MULTIPLE,
                        params=SyncMultipleParams(
                            source_link=this_link,
                            visited_registries=visited_registries,
                            registry=to_link.registry,
                            values=values,
                        ),
                    )
                )
                .map(lambda r: r.sync_acceptance)
                .unwrap_or_else(lambda _: [SyncAcceptance(to_link, False)])
            )

    async def _call_sync_all(
        self,
        this_link: RegLink,
        visited_registries: list[RegLink],
        to_link: RegLink,
        values: dict[Regname, str],
    ) -> list[SyncAcceptance]:
        async with self.clients.client(to_link.instance) as client:
            return (
                (
                    await client.request(
                        descriptor=RegMethod.SYNC_ALL,
                        params=SyncAllParams(
                            source_link=this_link,
                            visited_registries=visited_registries,
                            registry=to_link.registry,
                            values=values,
                        ),
                    )
                )
                .map(lambda r: r.sync_acceptance)
                .unwrap_or_else(lambda _: [SyncAcceptance(to_link, False)])
            )
