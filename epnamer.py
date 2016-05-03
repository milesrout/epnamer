import json
import os
import re
import urllib.request


class ShowInfo:
    id = None
    name = None
    summary = None

class EpisodeInfo:
    season = None
    num = None
    name = None

    def __str__(self):
        return "{} s{:02}e{:02}".format(self.name, self.season, self.num)

def json_query(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.readall().decode('utf-8'))

def get_show_info(show_name):
    show_search_url = "http://api.tvmaze.com/singlesearch/shows?q={}"
    query_url = show_search_url.format(urllib.parse.quote(show_name))
    json_data = json_query(query_url)
    show_info = ShowInfo()
    show_info.id = json_data['id']
    show_info.name = json_data['name']
    show_info.summary = json_data['summary']
    return show_info

def confirm_show(show_info):
    print("Selected '{}'".format(show_info.name))
    print("'''{}'''".format(show_info.summary))
    print()
    return input("Correct? [Y/n] ").lower() in ('y', 'yes', '')

def get_episodes_info(show_id):
    episode_search_url = "http://api.tvmaze.com/shows/{}/episodes"
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

def extract_file_info(filename):
    epcode_re = re.compile(r"S(\d\d)E(\d\d)", re.IGNORECASE)
    match = epcode_re.search(filename)
    if match:
        return tuple(map(int, match.groups()))
    return None

def make_file_table(filenames, episodes):
    name_map = {}
    for filename in filenames:
        info = extract_file_info(filename)
        if info:
            name_map[info] = filename
    table = []
    for episode in episodes:
        key = episode.season, episode.num
        if key in name_map:
            table.append((name_map[key], episode))
    return table

def main():
    print("Data obtained via TVmaze <tvmaze.com>")

    show_name = "Friends"
    show_info = get_show_info(show_name)
    if confirm_show(show_info):
        episodes =  get_episodes_info(show_info.id)
        for row in make_file_table(os.listdir("test"), episodes):
            print(*row)

def generate_name(season, episode):
    return '{}.s{}e{}'.format(show_name, season, episode)

def get_name_map(old_filenames):
    epcode_re = re.compile(r"S(\d\d)E(\d\d)", re.IGNORECASE)
    name_map = {}
    for filename in old_filenames:
        match = epcode_re.search(filename)
        if match:
            name_map[filename] = generate_name(filename, *match.groups())

if __name__ == "__main__":
    main()
