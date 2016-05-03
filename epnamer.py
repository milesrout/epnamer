import json
import os
import re
import urllib.request

from collections import namedtuple

Episode = namedtuple('Episode', 's, e, title')

def _json_query(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.readall().decode('utf-8'))


class tvmaze_guide:
    def __init__(self, *args):
        self.episodes = []
        if args:
            self.fetch(*args)

    def __iter__(self):
        yield from self.episodes

    def _find_show_id(self, show_name):
        url = "http://api.tvmaze.com/singlesearch/shows?q={}"
        query = url.format(urllib.parse.quote(show_name))
        result = _json_query(query)
        return result['id']

    def _parse_episode(self, ep_data):
        return Episode(ep_data['season'], ep_data['number'], ep_data['name'])

    def fetch(self, show_name):
        show_id = self._find_show_id(show_name)
        url = "http://api.tvmaze.com/shows/{}/episodes"
        query = url.format(show_id)
        result = _json_query(query)
        for ep_result in result:
            self.episodes.append(self._parse_episode(ep_result))


