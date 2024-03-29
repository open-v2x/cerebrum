#   Copyright 99Cloud, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
"""DoNotPass Service."""
import asyncio
from fastapi import FastAPI  # type:ignore
from fastapi import WebSocket
import grpc.aio  # type:ignore
import json
from collision_service.algo.algo_lib import CollisionWarning
from grpc_server import collision_grpc_pb2
from grpc_server import collision_grpc_pb2_grpc
from pydantic import BaseModel  # type:ignore
from starlette.websockets import WebSocketDisconnect  # type:ignore
from typing import List, Dict, Any
import uvicorn  # type:ignore
from collision_service import constants

app = FastAPI()

collision = CollisionWarning()


class ConnectionManager:
    """Websocket connect manager."""

    def __init__(self):
        """init."""
        self.active_connections: List[WebSocket] = []  # noqa

    async def connect(self, websocket: WebSocket):
        """connect."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """disconnect."""
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send personal message."""
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        """broadcast."""
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


class CollisionModel(BaseModel):
    """model."""

    context_frames: dict
    current_frame: dict
    last_timestamp: int


@app.post("/collision")
async def post(data: CollisionModel):
    """http."""
    msg, show_info, last_timestamp, motors_trajs, vptc_trajs = collision.run(
        **data.dict()
    )
    return {
        "msg": msg,
        "info": show_info,
        "last_timestamp": last_timestamp,
        "motors_trajs": motors_trajs,
        "vptc_trajs": vptc_trajs,
    }


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):
    """websocket."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg, show_info, last_timestamp, motors_trajs, vptc_trajs = collision.run(**data)  # type: ignore
            await manager.send_personal_message(
                dict(
                    msg=msg,
                    info=show_info,
                    last_timestamp=last_timestamp,
                    motors_trajs=motors_trajs,
                    vptc_trajs=vptc_trajs,
                ),
                websocket,
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


class DoNotPassGrpc(collision_grpc_pb2_grpc.CollisionGrpcServicer):
    """grpc server."""

    async def collision(self, request, context):
        """Grpc server."""
        data = json.loads(request.data)
        (
            msg,
            show_info,
            last_timestamp,
            motors_trajs,
            vptc_trajs,
        ) = collision.run(**data)
        return collision_grpc_pb2.CollisionResponse(
            data=json.dumps(
                {
                    "msg": msg,
                    "info": show_info,
                    "last_timestamp": last_timestamp,
                    "motors_trajs": motors_trajs,
                    "vptc_trajs": vptc_trajs,
                }
            )
        )


@app.on_event("startup")
async def startup_event():
    """Grpc connect."""
    server = grpc.aio.server()
    collision_grpc_pb2_grpc.add_CollisionGrpcServicer_to_server(
        DoNotPassGrpc(), server
    )
    listen_addr = f"0.0.0.0:{constants.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    await server.start()
    print(f"Starting server on {listen_addr}")

    asyncio.ensure_future(server.wait_for_termination())


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=constants.HTTP_PORT)
