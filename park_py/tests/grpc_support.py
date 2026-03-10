from __future__ import annotations

from types import SimpleNamespace

import grpc


class AbortedRpcError(grpc.RpcError):
    def __init__(self, *, code: grpc.StatusCode, details: str) -> None:
        super().__init__()
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


class DirectRpcContext:
    def abort(self, code, details) -> None:
        raise AbortedRpcError(code=code, details=details)


def build_direct_stub(*, servicer, method_names: list[str]):
    def _invoke(method_name: str):
        def _caller(request, timeout=None):  # noqa: ARG001
            return getattr(servicer, method_name)(request, DirectRpcContext())

        return _caller

    return SimpleNamespace(
        **{
            method_name: _invoke(method_name)
            for method_name in method_names
        }
    )
