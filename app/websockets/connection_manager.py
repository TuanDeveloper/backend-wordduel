"""Room WebSocket connections with Redis Pub/Sub fan-out across workers."""

import asyncio
import json
import logging
from typing import Any
from uuid import uuid4

from fastapi import WebSocket
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    CHANNEL = "wordduel:rooms:broadcast"

    def __init__(self) -> None:
        self._rooms: dict[str, list[tuple[WebSocket, int]]] = {}
        self._instance_id = str(uuid4())
        self._redis: Redis | None = None
        self._listener_task: asyncio.Task | None = None

    async def connect(
        self,
        websocket: WebSocket,
        room_code: str,
        user_id: int,
        subprotocol: str = "wordduel",
    ) -> None:
        await websocket.accept(subprotocol=subprotocol)
        self._rooms.setdefault(room_code, []).append((websocket, user_id))
        self._ensure_listener()

    def disconnect(self, websocket: WebSocket, room_code: str) -> None:
        connections = self._rooms.get(room_code)
        if not connections:
            return
        remaining = [(ws, user_id) for ws, user_id in connections if ws is not websocket]
        if remaining:
            self._rooms[room_code] = remaining
        else:
            self._rooms.pop(room_code, None)

    async def broadcast(self, room_code: str, payload: Any) -> None:
        await self._broadcast_local(room_code, payload)
        self._ensure_listener()
        if self._redis is None:
            return
        envelope = json.dumps(
            {"origin": self._instance_id, "room_code": room_code, "payload": payload},
            ensure_ascii=False,
        )
        try:
            await self._redis.publish(self.CHANNEL, envelope)
        except Exception:
            logger.warning("Redis Pub/Sub publish failed; keeping broadcast local", exc_info=True)

    async def _broadcast_local(self, room_code: str, payload: Any) -> None:
        message = json.dumps(payload, ensure_ascii=False)
        dead: list[WebSocket] = []
        for websocket, _user_id in list(self._rooms.get(room_code, [])):
            try:
                await websocket.send_text(message)
            except Exception:
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(websocket, room_code)

    async def send_personal(self, websocket: WebSocket, payload: Any) -> None:
        await websocket.send_text(json.dumps(payload, ensure_ascii=False))

    def _ensure_listener(self) -> None:
        try:
            if self._redis is None:
                self._redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception:
            logger.warning("Redis Pub/Sub is unavailable; broadcasts remain local", exc_info=True)
            return
        if self._listener_task is None or self._listener_task.done():
            self._listener_task = asyncio.create_task(self._listen_for_broadcasts())

    async def _listen_for_broadcasts(self) -> None:
        while True:
            pubsub = None
            try:
                pubsub = self._redis.pubsub()
                await pubsub.subscribe(self.CHANNEL)
                while True:
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if not message or message.get("type") != "message":
                        continue
                    envelope = json.loads(message["data"])
                    if envelope.get("origin") != self._instance_id:
                        await self._broadcast_local(envelope["room_code"], envelope["payload"])
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.warning("Redis Pub/Sub listener disconnected; retrying", exc_info=True)
                if pubsub is not None:
                    try:
                        await pubsub.aclose()
                    except Exception:
                        pass
                await asyncio.sleep(2)

    async def shutdown(self) -> None:
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    def get_connected_user_ids(self, room_code: str) -> list[int]:
        return [user_id for _websocket, user_id in self._rooms.get(room_code, [])]

    def room_exists(self, room_code: str) -> bool:
        return bool(self._rooms.get(room_code))


manager = ConnectionManager()
