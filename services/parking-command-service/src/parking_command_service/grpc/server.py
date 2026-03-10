from __future__ import annotations

from concurrent import futures

import grpc

from contracts.gen.python.parking_command.v1 import parking_command_pb2_grpc
from parking_command_service.grpc.servicers import ParkingCommandGrpcServicer


def build_parking_command_grpc_server(
    *,
    servicer: ParkingCommandGrpcServicer | None = None,
) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    parking_command_pb2_grpc.add_ParkingCommandServiceServicer_to_server(
        servicer or ParkingCommandGrpcServicer(),
        server,
    )
    return server
