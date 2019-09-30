#!/usr/bin/env python3

import time
import datetime
import sys
import pycron
import wekan_scheduler
from settings.config import CONFIG
from settings.schedules import SCHEDULES


from pprint import pprint

def create_card(_sched):
    # create a work copy
    sched = _sched.copy()

    # Wekan API wrapper
    api = wekan_scheduler.api()

    # add authorId if missing
    if not 'authorId' in sched['card']:
        sched['card']['authorId'] = api.user_id

    # add swimlaneId if missing
    if not 'swimlaneId' in sched['card']:
        sl = api.api_call("/api/boards/{}/swimlanes".format(sched['board']))
        sched['card']['swimlaneId'] = sl[0]['_id']

    # create card
    res = api.api_call(
        "/api/boards/{}/lists/{}/cards".format(sched['board'], sched['list']), sched['card'])

    # add details
    if '_id' in res:
        # check details field for callables
        for k, v in sched['details'].items():
            if callable(v):
                sched['details'][k] = v()

        api_response = api.session.put(
            "{}{}".format(api.api_url, "/api/boards/{}/lists/{}/cards/{}".format(
                sched['board'], sched['list'], res['_id'])),
            data=sched['details'],
            headers={"Authorization": "Bearer {}".format(api.token)},
            proxies=api.proxies
        )

sinces = {}
for idx, sched in enumerate(SCHEDULES):
    sinces[idx] = datetime.datetime.now()

def main():
    print("#- SCHEDULER IS ALIVE")
    while True:
        for idx, sched in enumerate(SCHEDULES):
            ts = datetime.datetime.now()
            if pycron.has_been(sched['schedule'], sinces[idx]):
                try:
                    print("#{} RUNNING SCHEDULE".format(idx + 1))
                    create_card(sched)
                    sinces[idx] = ts
                    print("#{} => DONE".format(idx + 1))
                except:
                    print("#{} => EXCEPTION: {}".format(idx + 1, sys.exc_info()))

        time.sleep(CONFIG['sleep'])

if __name__ == "__main__":
    if CONFIG['api_verify']:
        main()
    else:
        with wekan_scheduler.no_ssl_verification():
            main()
