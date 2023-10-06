import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

# from channels.asgi import get_channel_layer

from .models import Service, Visitor


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print(f"+ {clean_channel_name(self.channel_name)}")

        await self.accept()
        await self.send_json(
            {
                "type": "status",
                "message": "Waiting for token",
            }
        )

    async def disconnect(self, code):
        print(f"- {clean_channel_name(self.channel_name)} ({code})")

        group = self.scope.get("host_group")
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

        group = self.scope.get("client_group")
        if group:
            await self.channel_layer.group_discard(group, self.channel_name)

        await self.on_group_update()
        await super().disconnect(code)

    async def send_data(self, event):
        await self.send_json(event["data"])

    async def on_group_update(self):
        data = {"type": "users", "host": [], "client": []}

        host_group_name = self.scope.get("host_group")
        if host_group_name in self.channel_layer.groups:
            users = self.channel_layer.groups[host_group_name]
            users = {clean_channel_name(name): users[name] for name in users}
            data["host"] = users

        client_group_name = self.scope.get("client_group")
        if client_group_name in self.channel_layer.groups:
            users = self.channel_layer.groups[client_group_name]
            users = {clean_channel_name(name): users[name] for name in users}
            data["client"] = users

        await self.channel_layer.group_send(
            host_group_name,
            {"type": "send_data", "data": data},
        )
        await self.channel_layer.group_send(
            client_group_name,
            {"type": "send_data", "data": data},
        )

    async def receive_json(self, content):
        print(">", str(content))
        if not self.authorized:
            return await self.authenticate(content)

        await self.channel_layer.group_send(
            self.get_target_group(),
            {"type": "send_data", "data": content},
        )

    async def authenticate(self, content):
        token = content.get("token", None)
        if not token:
            self.send_json({"type": "error", "error": "Unauthorized"})
            return await self.close()

        if not await self.check_token(token):
            await self.send_json({"type": "error", "error": "Invalid token"})
            return await self.close()

        is_host = self.scope.get("host")

        if is_host:
            await self.channel_layer.group_add(
                self.scope.get("host_group"),
                self.channel_name,
            )
        else:
            await self.channel_layer.group_add(
                self.scope.get("client_group"),
                self.channel_name,
            )

        if is_host:
            await self.send_json({"type": "status", "message": "Authorized as server"})
        else:
            await self.send_json({"type": "status", "message": "Authorized as client"})

        await self.on_group_update()

    async def check_token(self, token):
        host_service = await self.get_host_service(token)
        if host_service:
            print("?????", host_service, host_service.host_token)
            self.scope["host_token"] = host_service.host_token
            self.scope["authorized"] = True
            self.scope["host"] = True
            self.scope["guest"] = False
            self.scope["host_group"] = host_service.host_group
            self.scope["client_group"] = host_service.client_group
            return True

        client_service = await self.get_client_service(token)
        if client_service:
            self.scope["host_token"] = client_service.host_token
            self.scope["authorized"] = True
            self.scope["host"] = False
            self.scope["guest"] = False
            self.scope["host_group"] = client_service.host_group
            self.scope["client_group"] = client_service.client_group
            return True

        return False

    def get_target_group(self):
        if self.scope.get("host"):
            return self.scope.get("client_group")
        else:
            return self.scope.get("host_group")

    @property
    def authorized(self):
        return self.scope.get("authorized", False)

    @database_sync_to_async
    def get_host_service(self, token):
        if Service.objects.filter(host_token=token).exists():
            return Service.objects.get(host_token=token)

    @database_sync_to_async
    def get_client_service(self, token):
        if Service.objects.filter(client_token=token).exists():
            return Service.objects.get(client_token=token)


def clean_channel_name(name):
    return name.split("!")[1]
