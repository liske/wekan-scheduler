# Wekan Scheduler

Pythonic card scheduler for [Wekan](https://wekan.github.io/).


## About

The purpose of *wekan-scheduler* is to create cards regulary for repeating
tasks. It uses [pycron](https://github.com/kipe/pycron) for schedule
configuration and uses the
[wekan-python-api-client](https://github.com/wekan/wekan-python-api-client) to
access the [Wekan REST API](https://wekan.github.io/api/v3.00/).


## Configuration

You should create a dedicated user in *Wekan* to be used to access the *Wekan
REST API* in the `PASSWORD` auth backend (`LDAP` seems not to work). Add the
user to the boards where it should create cards.

There are three configuration files required in the `settings` directory:

- **\_\_init\_\_.py**
  should left empty, required to make the config a python package
- **config.py**
  contains the base configuration to access the *Wekan REST API*:
  ```python
  CONFIG = {
    # URL for Wekan
    'api_url': "https://localhost/kanban",

    # REST API auth headers
    'api_auth': {"username": "api", "password": "xxxxxxxx"},

    # Verify X.509 certificate for api_url?
    'api_verify': True,

    # Sleep for N seconds between schedules (should be at least 60s)
    'sleep': 300,
  }
  ```
- **schedules.py**
  contains your custom schedules:
  ```python
  import datetime
  import pytz

  SCHEDULES = [
    # daily work card
    {
        # cron-like schedule (pycron)
        'schedule': '0 8 * * 1-5',

        # target board and list
        'board': '<board-id>',
        'list': '<list-id>',

        # required fields
        'card': {
            'title': 'check for donuts',
        },

        # more card details
        'details': {
            'description': 'first-come, first-served',
            'color': 'pink',
            'labelIds': ['<label-id>'],
            # set due time at 17 o'clock tomorrow
            #'dueAt': lambda: (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0).astimezone(pytz.utc).isoformat(),
            'members': ['<user-id>'],
        },
    },
  ]
  ```
  If the value of a `details` dictonary item is a *callable* it is used to build
  the actual value of the item. This could be used to build dynamic due times.

There is a `get-ids.py` helper script to dump the various IDs of your Wekan
instance. This helps to find the required various IDs for your schedules:

```
{'boards': {'4b5BmHE2CL8wt8brR': {'labels': {'2kRvzr': 'gray[crumbly]',
                                             'jdiYNd': 'plum[goo]',
                                             'xhAdgq': 'lime[tasty]'},
                                  'lists': {'zzujS93kd8982k30y': 'Backlog',
                                            'loxc9Dll,masd300a': 'Eating',
                                            'qosLk34SDKsmsksd3': 'Done',
                                            'lasd93lkdaskSAKsl': 'Problem'},
                                  'title:': 'Donut Fighters'}},
 'users': [{'_id': 'Ksd34pKsW23wFg9Sx', 'username': 'admin'},
           {'_id': 'lS9lkasd3mAusdkSK', 'username': 'api'}]}
```


## Deploy

The recommended way to run *wekan-scheduler* is to use the provided auto-build
docker images from [Docker
Hub](https://cloud.docker.com/u/liske/repository/docker/liske/wekan-scheduler).
Run it with *docker-compose*:

```yaml
version: '3'

services:
  scheduler:
    image: liske/wekan-scheduler:0.1
    restart: always
    volumes:
      - ./settings:/app/wekan-scheduler/settings:ro
```

If you are running *Wekan* on *Docker* you may add *wekan-scheduler* to your
existing `docker-compose.yml`:

```yaml
  # ...
  scheduler:
    image: liske/wekan-scheduler:0.1
    restart: always
    volumes:
      - ./scheduler/settings:/app/wekan-scheduler/settings:ro
  depends_on:
    - wekan
  # ...
```
