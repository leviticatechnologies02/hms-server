import json
from collections import defaultdict
from typing import Dict, List
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect

class CorporateDashboardManager:
    """
    WebSocket Manager for Corporate Dashboard

    One Corporate Account
            │
    ┌───────┼────────┐
    │       │        │
    User1  User2   User3

    Every dashboard update is broadcast only
    to users belonging to the same Corporate Account.
    """

    def __init__(self):

        # Corporate -> WebSockets
        self.active_connections: Dict[
            UUID,
            List[WebSocket]
        ] = defaultdict(list)

    # Connect
    async def connect(
        self,
        websocket: WebSocket,
        corporate_account_id: UUID,
    ):

        await websocket.accept()

        self.active_connections[
            corporate_account_id
        ].append(websocket)

    # Disconnect
    def disconnect(
        self,
        websocket: WebSocket,
        corporate_account_id: UUID,
    ):

        if (
            corporate_account_id
            not in self.active_connections
        ):
            return

        if websocket in self.active_connections[
            corporate_account_id
        ]:
            self.active_connections[
                corporate_account_id
            ].remove(websocket)

        if len(
            self.active_connections[
                corporate_account_id
            ]
        ) == 0:
            del self.active_connections[
                corporate_account_id
            ]

    # Send Personal Message
    async def send_personal_message(
        self,
        websocket: WebSocket,
        message: dict,
    ):

        await websocket.send_json(message)

    # Broadcast
    async def broadcast(
        self,
        corporate_account_id: UUID,
        event: str,
        data: dict,
    ):

        if (
            corporate_account_id
            not in self.active_connections
        ):
            return

        payload = {
            "event": event,
            "data": data,
        }

        disconnected = []

        for connection in self.active_connections[
            corporate_account_id
        ]:

            try:

                await connection.send_json(payload)

            except Exception:

                disconnected.append(connection)

        for connection in disconnected:

            self.disconnect(
                connection,
                corporate_account_id,
            )

    # Dashboard Refresh
    async def refresh_dashboard(
        self,
        corporate_account_id: UUID,
        dashboard_data: dict,
    ):

        await self.broadcast(
            corporate_account_id,
            "dashboard_refresh",
            dashboard_data,
        )

    # KPI Update
    async def kpi_updated(
        self,
        corporate_account_id: UUID,
        kpi: dict,
    ):

        await self.broadcast(
            corporate_account_id,
            "kpi_updated",
            kpi,
        )

    # Revenue Update
    async def revenue_updated(
        self,
        corporate_account_id: UUID,
        revenue: dict,
    ):

        await self.broadcast(
            corporate_account_id,
            "revenue_updated",
            revenue,
        )

    # Hospital Status
    async def hospital_status_changed(
        self,
        corporate_account_id: UUID,
        hospital: dict,
    ):

        await self.broadcast(
            corporate_account_id,
            "hospital_status",
            hospital,
        )

    # Notification
    async def notification(
        self,
        corporate_account_id: UUID,
        notification: dict,
    ):

        await self.broadcast(
            corporate_account_id,
            "notification",
            notification,
        )

    # Subscription Update
    async def subscription_updated(
        self,
        corporate_account_id: UUID,
        subscription: dict,
    ):

        await self.broadcast(
            corporate_account_id,
            "subscription_updated",
            subscription,
        )

    # Audit Event
    async def audit_event(
        self,
        corporate_account_id: UUID,
        audit: dict,
    ):

        await self.broadcast(
            corporate_account_id,
            "audit_event",
            audit,
        )

    # System Alert
    async def system_alert(
        self,
        corporate_account_id: UUID,
        alert: dict,
    ):

        await self.broadcast(
            corporate_account_id,
            "system_alert",
            alert,
        )

    # Ping
    async def ping(
        self,
        websocket: WebSocket,
    ):

        await websocket.send_json(
            {
                "event": "ping",
                "message": "alive",
            }
        )
    # Receive Loop
    async def websocket_endpoint(
        self,
        websocket: WebSocket,
        corporate_account_id: UUID,
    ):

        await self.connect(
            websocket,
            corporate_account_id,
        )
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                if message.get("event") == "ping":
                    await self.ping(websocket)
        except WebSocketDisconnect:
            self.disconnect(
                websocket,
                corporate_account_id,
            )

        except Exception:
            self.disconnect(
                websocket,
                corporate_account_id,
            )

dashboard_manager = CorporateDashboardManager()