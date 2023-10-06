# Omni

A communication server that connects applications over WebSocket. More info to come.

## Prerequisites

Before getting started you should have the following installed and running:

- [X] Python 3.10
- [X] Pipenv

## Installation

```
$ git clone git@gitlab.liu.se:C/General/remote-interaction/omni.git
$ cd omni
$ pipenv install
$ pipenv shell
$ python manage.py migrate --run-syncdb
$ python manage.py createsuperuser
$ python manage.py runserver
```

Then visit http://localhost:8000/admin/
