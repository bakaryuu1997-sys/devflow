"""Aggregate every ``app.routes_*`` module into a single :class:`APIRouter`.

Historically this file listed ~130 lines of hand-maintained imports, one per
versioned route module (``routes_v4`` … ``routes_v120``). That list had to be
edited by hand every time a module was added, which was error prone. Instead we
discover the route modules dynamically and include them in a deterministic
order so behaviour is identical to the old explicit list.

Ordering rules (kept stable so overlapping paths resolve the same way):
1. The foundational routers first, in the historical order.
2. Then the versioned ``routes_v<N>`` modules sorted numerically by ``<N>``.
"""

from __future__ import annotations

import importlib
import pkgutil
import re

from fastapi import APIRouter

import app as _app_pkg

# Foundational routers included ahead of the versioned ones, in historical order.
_PRIORITY = ["routes_auth", "routes_core", "routes_os", "routes_guards", "routes_security"]
_VERSION_RE = re.compile(r"^routes_v(\d+)$")


def _discover_route_modules() -> list[str]:
    """Return every ``routes_*`` module name except this aggregator."""
    names = [
        name
        for _, name, _ in pkgutil.iter_modules(_app_pkg.__path__)
        if name.startswith("routes_")
    ]

    def sort_key(name: str) -> tuple[int, int, str]:
        if name in _PRIORITY:
            return (0, _PRIORITY.index(name), name)
        match = _VERSION_RE.match(name)
        if match:
            return (1, int(match.group(1)), name)
        return (2, 0, name)  # any other routes_* module, alphabetical

    return sorted(names, key=sort_key)


_WIRED_MODULES: list[str] = []


def build_router() -> APIRouter:
    aggregate = APIRouter()
    _WIRED_MODULES.clear()
    for module_name in _discover_route_modules():
        module = importlib.import_module(f"app.{module_name}")
        sub_router = getattr(module, "router", None)
        if isinstance(sub_router, APIRouter):
            aggregate.include_router(sub_router)
            _WIRED_MODULES.append(module_name)
    return aggregate


def wired_route_modules() -> list[str]:
    """Names of the ``routes_*`` modules actually included in the app router.

    Exposed so tests can assert a version is wired by behaviour (it was
    discovered and included) instead of grepping this file's source text.
    """
    return list(_WIRED_MODULES)


router = build_router()
