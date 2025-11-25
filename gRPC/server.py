import grpc
import asyncio
from grpc import aio
from .CloudRoute_pb2_grpc import add_CloudRouteServicer_to_server
from .cloud_route_service import CloudRouteService
from detection.model.yolo.yolo_detection import YOLODetectionService


def load_server_credentials(cert_path, key_path):
    with open(cert_path, "rb") as f:
        cert_chain = f.read()
    with open(key_path, "rb") as f:
        private_key = f.read()

    return grpc.ssl_server_credentials(
        [(private_key, cert_chain)],
        root_certificates=None,
        require_client_auth=False
    )


async def serve():
    print("🚀 Starting CloudRoute gRPC server (ASYNC)...")

    # ASYNC gRPC SERVER (REQUIRED FOR STREAMING)
    server = aio.server()

    # Load YOLO model
    model = YOLODetectionService("yolo11n.pt")

    # Register service
    add_CloudRouteServicer_to_server(
        CloudRouteService(cloud_model=model),
        server
    )

    # Load TLS
    creds = load_server_credentials("gRPC/server.crt", "gRPC/server.key")
    print("🔒 Loaded TLS certificate and key")

    port = server.add_secure_port("[::]:50051", creds)
    print(f"📡 gRPC server bound to port {port}")

    await server.start()
    print("✅ gRPC server started successfully")

    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
