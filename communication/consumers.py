import json, random, uuid
from redis import Redis
from django.core.exceptions import ValidationError
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels_redis.core import RedisChannelLayer
from .utils import is_uuid, explain_websocket_code

from .models import Service, Visitor


class OmniConsumer(AsyncJsonWebsocketConsumer):
    channel_layer: RedisChannelLayer

    authorized = False
    is_host = False
    is_guest = False
    allow_public_code = False
    allow_multiple_hosts = False
    host_token = None
    host_group = None
    client_group = None
    guest_group = None

    def __init__(self, *args, **kwargs):
        super(OmniConsumer, self).__init__(*args, **kwargs)
        assert self.host_token is None

    async def connect(self):
        print(f"+ {self} Connected")

        await self.accept()
        await self.send_json(
            {"type": "server_connect", "message": "Welcome! Please provide a token."}
        )

    async def disconnect(self, code):
        print(f"- {self} Disconnected ({explain_websocket_code(code)})")

        if self.is_host:
            # Clear service code
            if code != 4000:
                await self.clear_public_code()
                print(f"$ {self} Cleared public code")

            # Annouce departure to clients
            await self.channel_layer.group_send(
                self.guest_group,
                {"type": "on_kick", "message": "Session ended by host"},
            )

        if self.host_group:
            await self.channel_layer.group_discard(self.host_group, self.channel_name)

        if self.client_group:
            await self.channel_layer.group_discard(self.client_group, self.channel_name)

        if self.guest_group:
            await self.channel_layer.group_discard(self.guest_group, self.channel_name)

        # Announce that channel left
        if self.authorized:
            await self.channel_layer.group_send(
                self.other_group,
                {"type": "on_leave", "role": self.title, "user": self.short_name},
            )

        await super().disconnect(code)

    async def receive_json(self, content):
        # print(f"> {self} {content}")

        # Check if message is not in JSON format
        if not isinstance(content, dict):
            print(f"> {self} {content}")
            await self.send_json(
                {"type": "server_error", "message": "Malformed message. Expected JSON."}
            )
            return await self.close()

        # If new user, check token first and authenticate them
        if not self.authorized:
            print(f"> {self} {content}")
            return await self.authenticate(content)

        # Add additional data about the sender
        if not self.is_host:
            content["user"] = self.short_name

        await self.channel_layer.group_send(
            self.other_group,
            {"type": "on_send", "data": content},
        )

    async def send_json(self, content, close=False):
        # print(f"< {self} {content}")
        await super().send_json(content, close)

    # Authentication check for the user's first message
    async def authenticate(self, content):
        # Check if token is provided
        token = content.get("token", None)
        if not token:
            message = 'Unauthorized. Expected {"token": "<token>"}'
            await self.send_json({"type": "server_error", "message": message})
            return await self.close()

        # Check if token is valid
        if not await self.check_token(token):
            message = "Invalid token"
            await self.send_json({"type": "server_error", "message": message})
            return await self.close()

        # Force existing host to leave
        if self.is_host and not self.allow_multiple_hosts:
            await self.channel_layer.group_send(
                self.my_group,
                {"type": "on_kick", "message": "Kicked by new host"},
            )

        # Subscribe to group
        await self.channel_layer.group_add(self.my_group, self.channel_name)
        print(f"+ {self} Subscribed to '{self.my_group}'")
        if self.is_guest:
            await self.channel_layer.group_add(self.guest_group, self.channel_name)
            print(f"+ {self} Subscribed to '{self.guest_group}'")

        # Successful authentication response
        message = f"Authorized as {self.title}"
        await self.send_json({"type": "server_authorized", "message": message})

        # Generate new public code
        if self.is_host and self.allow_public_code:
            code = await self.generate_public_code()
            if code:
                await self.send_json({"type": "server_code", "code": code})
                print(f"$ {self} Generated public code: {code}")

        # Announce that channel joined
        await self.channel_layer.group_send(
            self.other_group,
            {"type": "on_join", "role": self.title, "user": self.short_name},
        )

    # Check if token matches a service
    async def check_token(self, token):
        service = await self.find_service(token)
        if service:
            self.authorized = True
            self.host_token = service.host_token
            self.host_group = service.host_group
            self.client_group = service.client_group
            self.guest_group = service.guest_group

            if self.is_host:
                self.allow_public_code = service.allow_public_code
                self.allow_multiple_hosts = service.allow_multiple_hosts
            return True
        return False

    # Group send functions

    async def on_send(self, event):
        await self.send_json(event["data"])

    async def on_kick(self, event):
        await self.send_json({"type": "server_disconnect", "message": event["message"]})
        return await self.close(4000)

    async def on_join(self, event):
        await self.send_json(
            {"type": "server_join", "role": event["role"], "user": event["user"]}
        )

    async def on_leave(self, event):
        await self.send_json(
            {"type": "server_leave", "role": event["role"], "user": event["user"]}
        )

    # Django database

    @database_sync_to_async
    def find_service(self, token):
        if is_uuid(token):
            # Check if token is a host token
            if Service.objects.filter(host_token=token).exists():
                self.is_host = True
                return Service.objects.get(host_token=token)
            # Check if token is a client token
            if Service.objects.filter(client_token=token).exists():
                return Service.objects.get(client_token=token)
        elif isinstance(token, str):
            # Check if token is a public code
            if Service.objects.filter(public_code=token).exists():
                self.is_guest = True
                return Service.objects.get(public_code=token)

    @database_sync_to_async
    def generate_public_code(self):
        if Service.objects.filter(host_token=self.host_token).exists():
            service = Service.objects.get(host_token=self.host_token)
            if service.allow_public_code:
                return service.generate_code()

    @database_sync_to_async
    def clear_public_code(self):
        if Service.objects.filter(host_token=self.host_token).exists():
            service = Service.objects.get(host_token=self.host_token)
            service.clear_code()

    # Redis database

    @property
    def redis(self) -> Redis:
        index: int = self.channel_layer.consistent_hash(self.host_group)
        return self.channel_layer.connection(index)

    async def redis_get(self, key, default=None):
        group_key = f"{self.host_group}:{key}"
        value = await self.redis.get(group_key)
        if value is None:
            return default
        return json.loads(value)

    async def redis_set(self, key, value, expire_seconds=43200):
        group_key = f"{self.host_group}:{key}"
        await self.redis.set(group_key, json.dumps(value), expire_seconds)

    async def redis_delete(self, key):
        group_key = f"{self.host_group}:{key}"
        await self.redis.delete(group_key)

    async def redis_get_group(self, group):
        key = self.channel_layer._group_key(group)
        return await self.redis.zrange(key, 0, 100)

    # Properties

    @property
    def my_group(self):
        if self.is_host:
            return self.host_group
        else:
            return self.client_group

    @property
    def other_group(self):
        if self.is_host:
            return self.client_group
        else:
            return self.host_group

    @property
    def title(self):
        if self.is_host:
            return "host"
        elif self.is_guest:
            return "guest"
        else:
            return "client"

    @property
    def short_name(self):
        return self.channel_name.split("!")[1][:6]

    def __str__(self):
        return f"[{self.short_name}]"
