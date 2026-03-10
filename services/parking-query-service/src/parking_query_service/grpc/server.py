from __future__ import annotations

from concurrent import futures

import grpc

from contracts.gen.python.parking_query.v1 import parking_query_pb2_grpc
from parking_query_service.grpc.servicers import ParkingQueryGrpcServicer


def build_parking_query_grpc_server(
    *,
    servicer: ParkingQueryGrpcServicer | None = None,
) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    parking_query_pb2_grpc.add_ParkingQueryServiceServicer_to_server(
        servicer or ParkingQueryGrpcServicer(),
        server,
    )
    return server
