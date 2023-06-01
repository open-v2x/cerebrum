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
"""Reverse Driving Service."""
import asyncio
from fastapi import FastAPI  # type:ignore
from fastapi import WebSocket
import grpc.aio  # type:ignore
import json
from pydantic import BaseModel  # type:ignore

from reverse_driving_service.algo.algo_lib import ReverseDrivingWarning
from reverse_driving_service.grpc_server import reverse_driving_grpc_pb2
from reverse_driving_service.grpc_server import reverse_driving_grpc_pb2_grpc
from starlette.websockets import WebSocketDisconnect  # type:ignore
from typing import List
import uvicorn  # type:ignore

app = FastAPI()

reverse_driving = ReverseDrivingWarning()


"""*********** websocket **************"""


class ConnectionManager:
    """Websocket connect manager."""

    def __init__(self):
        """init."""
        self.active_connections: List[WebSocket] = []  # type: ignore

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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """websocket."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            rdw, show_info = reverse_driving.run(**data)  # type: ignore
            await manager.send_personal_message(
                dict(rdw=rdw, info=show_info), websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


"""*********** http **************"""


class ReverseDrivingModel(BaseModel):
    """model."""

    context_frames: dict
    current_frame: dict
    last_timestamp: int
    lane_info: dict


@app.post("/reverse_driving")
async def post(data: ReverseDrivingModel):
    """http."""
    rdw, show_info = reverse_driving.run(**data.dict())
    return json.dumps({"rdw": rdw, "info": show_info})


"""*********** grpc **************"""


class ReverseDriving(reverse_driving_grpc_pb2_grpc.ReverseDrivingGrpcServicer):
    """grpc server."""

    async def reverse_driving(self, request, context):
        """Grpc server."""
        data = json.loads(request.data)
        rdw, show_info = reverse_driving.run(**data)
        return reverse_driving_grpc_pb2.ReverseDrivingResponse(
            data=json.dumps({"rdw": rdw, "info": show_info})
        )


@app.on_event("startup")
async def startup_event():
    """Grpc connect."""
    server = grpc.aio.server()
    reverse_driving_grpc_pb2_grpc.add_ReverseDrivingGrpcServicer_to_server(
        ReverseDriving(), server
    )
    listen_addr = "0.0.0.0:28309"
    server.add_insecure_port(listen_addr)
    await server.start()
    print(f"Starting server on {listen_addr}")

    asyncio.ensure_future(server.wait_for_termination())


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=28307)
