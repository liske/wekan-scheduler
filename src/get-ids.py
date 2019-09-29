#!/usr/bin/env python3

from pprint import pprint
import wekan_scheduler
from settings.config import CONFIG


def get_ids():
    api = wekan_scheduler.api()

    ids = {
        'users': api.api_call("/api/users"),
        'boards': {},
    }

    for board in api.get_user_boards():
        if board.title == 'Templates':
            continue

        ids['boards'][board.id] = {'title:': board.title, 'labels': {}, 'lists': {}}
        
        data = api.api_call("/api/boards/{}".format(board.id))
        for label in data['labels']:
            ids['boards'][board.id]['labels'][label['_id']] = '{}[{}]'.format(label['color'], label.get('name', ''))

        for cardlist in board.get_cardslists():
            ids['boards'][board.id]['lists'][cardlist.id] = cardlist.title

    return ids


if __name__ == "__main__":
    if CONFIG['api_verify']:
        pprint(get_ids())
    else:
        with wekan_scheduler.no_ssl_verification():
            pprint(get_ids())
