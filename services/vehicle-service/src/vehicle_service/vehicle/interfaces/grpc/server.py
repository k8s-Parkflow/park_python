from __future__ import annotations

from concurrent import futures

import grpc

from contracts.gen.python.vehicle.v1 import vehicle_pb2_grpc
from vehicle_service.vehicle.interfaces.grpc.servicers import VehicleGrpcServicer


def build_vehicle_grpc_server(*, servicer: VehicleGrpcServicer | None = None) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    vehicle_pb2_grpc.add_VehicleServiceServicer_to_server(
        servicer or VehicleGrpcServicer(),
        server,
    )
    return server
