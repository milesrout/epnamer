import json
import os
import re
import urllib.request

target_dir = "~/epnamer/test"

show_search_url = "http://api.tvmaze.com/singlesearch/shows?q={}"
episode_search_url = "http://api.tvmaze.com/shows/{}/episodes"

epcode_re = re.compile(r"S(\d\d)E(\d\d)", re.IGNORECASE)


class ShowInfo:
    id = None
    name = None
    summary = None

class EpisodeInfo:
    season = None
    num = None
    name = None

def json_query(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.readall().decode('utf-8'))

def get_show_info(show_name):
    query_url = show_search_url.format(urllib.parse.quote(show_name))
    json_data = json_query(query_url)
    show_info = ShowInfo()
    show_info.id = json_data['id']
    show_info.name = json_data['name']
    show_info.summary = json_data['summary']
    return show_info

def confirm_show(show_info):
    print("Data obtained via TVmaze <tvmaze.com>")
    print("Selected '{}'".format(show_info.name))
    print("'''{}'''".format(show_info.summary))
    print()
    return input("Correct? [Y/n] ").lower() in ('y', 'yes', '')

def get_episodes_info(show_id):
    query_url = episode_search_url.format(show_id)
    json_data = json_query(query_url)
    episodes_info = []
    for episode_data in json_data:
        episode_info = EpisodeInfo()
        episode_info.season = episode_data['season']
        episode_info.num = episode_data['number']
        episode_info.name = episode_data['name']
        episodes_info.append(episode_info)
    return episodes_info

def main():
    show_name = "Penn & Teller Bullshit!"
    show_info = get_show_info(show_name)
    print(confirm_show(show_info))

    for ep in get_episodes_info(show_info.id):
        print(ep.name)

def generate_name(season, episode):
    return '{}.s{}e{}'.format(show_name, season, episode)

def get_name_map(old_filenames):
    name_map = {}
    for filename in old_filenames:
        match = epcode_re.search(filename)
        if match:
            name_map[filename] = generate_name(filename, *match.groups())

if __name__ == "__main__":
    main()
