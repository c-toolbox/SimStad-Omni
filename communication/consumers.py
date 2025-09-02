import json, random, uuid
from redis import Redis
from django.core.exceptions import ValidationError
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels_redis.core import RedisChannelLayer
from .utils import is_uuid, explain_websocket_code

from .models import Service, Session


class OmniConsumer(AsyncJsonWebsocketConsumer):
    channel_layer: RedisChannelLayer

    authorized = False
    is_host = False
    is_guest = False
    allow_public_code = False
    session_code = None
    host_token = None
    host_group = None
    client_group = None
    guest_group = None

    def __init__(self, *args, **kwargs):
        super(OmniConsumer, self).__init__(*args, **kwargs)
        assert self.host_token is None

    async def connect(self):
        print(f"+ {self} Connected")

        # headers = self.scope.get("headers")
        # if headers:
        #     host_header = next((value for key, value in headers if key == b'host'), None)
        #     if host_header:
        #         print(f"Host header found: {host_header}")

        await self.accept()
        await self.send_json(
            {"type": "server_connect", "message": "Welcome! Please provide a token."}
        )

    async def disconnect(self, code):
        print(f"- {self} Disconnected ({explain_websocket_code(code)})")

        if self.is_host:
            # Clear service code
            if code != 4000:
                await self.clear_session(self.session_code)

            # Annouce departure to clients
            await self.channel_layer.group_send(
                self.guest_group,
                {"type": "on_kick", "message": "Session ended by host"},
            )

        # Remove the user's channel name from Redis
        await self.redis_delete(f"user:{self.short_name}")

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

        # Set message sender id
        target_user = content.get("user")
        if not self.is_host:
            content["user"] = self.short_name

        # If the message has a targeted user, send the message to the specific user's channel
        if target_user and self.is_host:
            channel_name = await self.redis_get(f"user:{target_user}")
            if channel_name:
                return await self.channel_layer.send(
                    channel_name,
                    {"type": "on_send", "data": content},
                )
            else:
                return await self.send_json(
                    {"type": "server_error", "message": f"User {target_user} not found"}
                )

        # Broadcast the message to the group
        return await self.channel_layer.group_send(
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
        if self.is_host and not self.allow_public_code:
            await self.channel_layer.group_send(
                self.my_group,
                {"type": "on_kick", "message": "Kicked by new host"},
            )

        # Find existing session or create a new one
        session = await self.find_session(token)
        if self.is_host and self.allow_public_code:
            session = await self.create_session()
        elif not session:
            self.authorized = False
            message = "Unable to join session"
            await self.send_json({"type": "server_error", "message": message})
            return await self.close()

        # Announce public code
        if self.is_host and self.allow_public_code:
            await self.send_json({"type": "server_code", "code": session.code})
            print(f"$ {self} Created new session: {session.code}")

        # Set session groups
        self.session_code = session.code
        self.host_group = session.host_group
        self.client_group = session.client_group
        self.guest_group = session.guest_group

        # Subscribe to group
        await self.channel_layer.group_add(self.my_group, self.channel_name)
        print(f"+ {self} Subscribed to '{self.my_group}'")
        if self.is_guest:
            await self.channel_layer.group_add(self.guest_group, self.channel_name)
            print(f"+ {self} Subscribed to '{self.guest_group}'")

        # Successful authentication response
        message = f"Authorized as {self.title}"
        await self.send_json({"type": "server_authorized", "message": message})

        # Announce that channel joined
        await self.channel_layer.group_send(
            self.other_group,
            {
                "type": "on_join",
                "role": self.title,
                "user": self.short_name,
                "name": content.get("name", None),
            },
        )

        # Store the user's channel name in Redis
        await self.redis_set(f"user:{self.short_name}", self.channel_name)

    # Check if token matches a service
    async def check_token(self, token):
        service = await self.find_service(token)
        if service:
            self.authorized = True
            self.host_token = service.host_token
            self.allow_public_code = service.allow_public_code
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
            {
                "type": "server_join",
                "role": event["role"],
                "user": event["user"],
                "name": event["name"],
            }
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
            if Session.objects.filter(code=token).exists():
                self.is_guest = True
                session = Session.objects.get(code=token)
                if session.service.allow_public_code:
                    return session.service

    @database_sync_to_async
    def create_session(self):
        if Service.objects.filter(host_token=self.host_token).exists():
            service = Service.objects.get(host_token=self.host_token)
            return service.add_session()

    @database_sync_to_async
    def find_session(self, token):
        if is_uuid(token):
            # Fetch service from token
            service = None
            if Service.objects.filter(host_token=token).exists():
                service = Service.objects.get(host_token=token)
            elif Service.objects.filter(client_token=token).exists():
                service = Service.objects.get(client_token=token)

            # Return existing session or create a new one
            if service and Session.objects.filter(service=service).exists():
                return Session.objects.filter(service=service).first()

        # If token is a public code, find the session
        elif isinstance(token, str) and self.allow_public_code:
            if Session.objects.filter(code=token).exists():
                return Session.objects.get(code=token)

    @database_sync_to_async
    def clear_session(self, session_code):
        if Session.objects.filter(code=session_code).exists():
            session = Session.objects.get(code=session_code)
            session.delete()
            print(f"- {self} Clearing session {session_code}")
        else:
            print(f"- {self} Cannot clear session {session_code}")

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
