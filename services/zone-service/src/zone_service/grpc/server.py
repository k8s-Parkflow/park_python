from __future__ import annotations

from concurrent import futures

import grpc

from contracts.gen.python.zone.v1 import zone_pb2_grpc
from zone_service.grpc.servicers import ZoneGrpcServicer


def build_zone_grpc_server(*, servicer: ZoneGrpcServicer | None = None) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    zone_pb2_grpc.add_ZoneServiceServicer_to_server(
        servicer or ZoneGrpcServicer(),
        server,
    )
    return server
