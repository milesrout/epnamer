import json
import os
import re
import urllib.request

target_dir = "~/epnamer/test"

show_search_url = "http://api.tvmaze.com/singlesearch/shows?q={}"

epcode_re = re.compile(r"S(\d\d)E(\d\d)", re.IGNORECASE)


class ShowInfo:
    id = None
    name = None
    summary = None

def generate_name(season, episode):
    return '{}.s{}e{}'.format(show_name, season, episode)

def get_name_map(old_filenames):
    name_map = {}
    for filename in old_filenames:
        match = epcode_re.search(filename)
        if match:
            name_map[filename] = generate_name(filename, *match.groups())


def get_show(show_name):
    query_url = show_search_url.format(urllib.parse.quote(show_name))
    with urllib.request.urlopen(query_url) as response:
        json_data = json.loads(response.readall().decode('utf-8'))
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

def main():
    show_name = "Penn & Teller Bullshit!"
    show_info = get_show(show_name)
    print(confirm_show(show_info))

if __name__ == "__main__":
    main()
