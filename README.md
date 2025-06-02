# Omni

A communication server that connects applications over WebSocket.

Website: https://omni.itn.liu.se/

## How to use

Omni allows applications to communicate with each other through a **service**. Upon connecting, the application must provide a service token to authenticate it as a **host** or **client**. A **guest** application may connect by providing a public code instead of a token.

### Terminology
- **Host**: An application acting as the exhibition - the star of the show.
- **Client**: A single user interface that interacts with the host. It can either be a touch table for visitors or a remote control for the speaker. Clients may connect to Omni before the host is online.
- **Guest**: A mobile website where multiple visitors can connect to the host using a public code. Guests are kicked when the host disconnects.

### Creating a service

In order to connect to Omni, you need a token belonging to a **service**. Each service has a unique **host-token** and **client-token**.

Services are handled here: https://omni.itn.liu.se/admin/. Ask Måns Gezelius for access.

### How to connect

- Connect your WebSocket to [wss://omni.itn.liu.se/ws/]()
    - Server response
        - `{"type": "server_connect", "message": "Welcome! Please provide a token."}`
- Authenticate as host
    - Send: `{"token": <HOST_TOKEN>}`
    - Server response:
        - `{"type": "server_authorized", "message": "Authorized as host"}`
        - `{"type": "server_code", <PUBLIC_CODE>}`
- Authenticate as client
    - Send: `{"token": <CLIENT_TOKEN>}`
    - Server response:
        - `{"type": "server_authorized", "message": "Authorized as client"}`
- Authenticate as guest
    - Send: `{"token": <PUBLIC_CODE>}`
        - Server response
            `{"type": "server_authorized", "message": "Authorized as guest"}`

Once connected, any further messages will be sent between connected hosts and clients. Messages must be in JSON format.

### Server responses

Omni provides additional messages

- `{"type": "server_connect", "message": "..."}`
    - Upon connecting successfully
- `{"type": "server_disconnect", "message": "..."}`
    - Upon forced disconnect, such as guests being kicked after host disconnects
- `{"type": "server_authorized", "message": message}`
    - Upon authorizing successfully
- `{"type": "server_code", "code": <PUBLIC_CODE>}`
    - Upon new public code being generated (when host authenticates)
- `{"type": "server_join", "role": "host/client/guest", "user": <USER_ID>}`
    - Upon new application connecting.
- `{"type": "server_leave", "role": "host/client/guest", "user": <USER_ID>}`
    - Upon application disconnecting.
- `{"type": "server_error", "message": "..."}`
    - Errors including non-json message sent or invalid token.

## Running Omni locally

### Prerequisites

- [x] Python 3.10 (Or edit Pipfile to your version)
- [x] Pipenv

### Installation

```
$ git clone git@gitlab.liu.se:C/General/remote-interaction/omni.git
$ cd omni
$ python -m pipenv install
$ python -m pipenv shell
$ python manage.py migrate --run-syncdb
$ python manage.py createsuperuser
$ python manage.py runserver
```

### Usage

Visit http://localhost:8000/admin/. Log in as superuser. Create a new service to generate a host-token and client-token.

Either install [Redis](https://redis.io/docs/install/install-redis/) locally or edit [/omni/settings/dev.py](https://gitlab.liu.se/C/General/remote-interaction/omni/-/blob/main/omni/settings/dev.py?ref_type=heads#L43) to use InMemoryChannelLayer instead.

Connect your WebSocket to [ws://localhost:8000/ws/](). Your first message must be `{"token": <TOKEN>}`.
