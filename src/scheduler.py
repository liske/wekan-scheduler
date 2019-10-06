#!/usr/bin/env python3

import time
import datetime
import os
import re
import sys
import ics
import pycron
import wekan_scheduler
from settings.config import CONFIG
from settings.schedules import SCHEDULES

from pprint import pprint


# check for calendar collisions
def match_ics(ics_fn=None, ics_event=None):
    for fn in os.listdir('ics'):
        if fn.endswith(".ics") and (ics_fn is None or re.match(ics_fn, fn)):
            with open(os.path.join('ics', fn)) as f:
                c = ics.Calendar(f)
                for ev in c.timeline.now():
                    if ics_event is None or re.match(ics_event, ev.name):
                        print("    calendar match 'in {}': {}".format(fn, ev.name))
                        return True
    return False


# create a card
def create_card(_sched):
    # do not create a card if calender has a matching event
    if 'ics' in _sched:
        if match_ics(_sched.get('fn'), _sched.get('event')):
            return

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

    # edit card stuff
    if '_id' in res:
        # add optional card details
        if 'details' in sched:
            # check details field for callables
            for k, v in sched['details'].items():
                if callable(v):
                    sched['details'][k] = v()

            api.session.put(
                "{}{}".format(api.api_url, "/api/boards/{}/lists/{}/cards/{}".format(
                    sched['board'], sched['list'], res['_id'])),
                data=sched['details'],
                headers={"Authorization": "Bearer {}".format(api.token)},
                proxies=api.proxies
            )

        # add optional checklists
        if 'checklists' in sched:
            for clname, items in sched['checklists']:
                api.api_call("/api/boards/{}/cards/{}/checklists".format(sched['board'], res['_id']),
                             {'title': clname,
                              'items': items,
                              })


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
                    print("#{} => EXCEPTION: {}".format(
                        idx + 1, sys.exc_info()))

        time.sleep(CONFIG['sleep'])


if __name__ == "__main__":
    if CONFIG['api_verify']:
        main()
    else:
        with wekan_scheduler.no_ssl_verification():
            main()
