"""
ConnectionManager - quan ly WebSocket connections theo room_code.

Moi phong co mot set cac WebSocket connections.
Khi broadcast, gui message toi tat ca connections trong phong.
Neu mot connection bi ngat, tu dong remove khoi danh sach.
"""
import asyncio
import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # room_code -> list of (websocket, user_id)
        self._rooms: dict[str, list[tuple[WebSocket, int]]] = {}

    # -- Ket noi / ngat ket noi -----------------------------------------

    async def connect(self, websocket: WebSocket, room_code: str, user_id: int) -> None:
        """Chap nhan ket noi WebSocket va them vao phong."""
        await websocket.accept()
        if room_code not in self._rooms:
            self._rooms[room_code] = []
        self._rooms[room_code].append((websocket, user_id))

    def disconnect(self, websocket: WebSocket, room_code: str) -> None:
        """Xoa connection khi client ngat ket noi."""
        if room_code in self._rooms:
            self._rooms[room_code] = [
                (ws, uid)
                for ws, uid in self._rooms[room_code]
                if ws is not websocket
            ]
            if not self._rooms[room_code]:
                del self._rooms[room_code]

    # -- Broadcast ------------------------------------------------------

    async def broadcast(self, room_code: str, payload: Any) -> None:
        """Gui JSON message toi tat ca connections trong phong."""
        if room_code not in self._rooms:
            return

        message = json.dumps(payload, ensure_ascii=False)
        dead: list[tuple[WebSocket, int]] = []

        for ws, uid in list(self._rooms.get(room_code, [])):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append((ws, uid))

        # Don connections loi
        for ws, uid in dead:
            self.disconnect(ws, room_code)

    async def send_personal(self, websocket: WebSocket, payload: Any) -> None:
        """Gui message rieng toi mot connection cu the."""
        message = json.dumps(payload, ensure_ascii=False)
        await websocket.send_text(message)

    # -- Utility --------------------------------------------------------

    def get_connected_user_ids(self, room_code: str) -> list[int]:
        """Danh sach user_id dang ket noi trong phong."""
        return [uid for _, uid in self._rooms.get(room_code, [])]

    def room_exists(self, room_code: str) -> bool:
        return room_code in self._rooms and len(self._rooms[room_code]) > 0


# Singleton - dung chung toan app
manager = ConnectionManager()
