import json
import os
import re
import urllib.request

target_dir = "~/epnamer/test"
show_name = "Penn & Teller Bullshit!"

show_search_url = "http://api.tvmaze.com/singlesearch/shows?q={}"

epcode_re = re.compile(r"S(\d\d)E(\d\d)", re.IGNORECASE)

def generate_name(season, episode):
    return '{}.s{}e{}'.format(show_name, season, episode)

def get_name_map(old_filenames):
    name_map = {}
    for filename in old_filenames:
        match = epcode_re.search(filename)
        if match:
            name_map[filename] = generate_name(filename, *match.groups())


def main():
    print("Data obtained via TVmaze <tvmaze.com>")
    dir_contents = os.listdir('test')
    #new_names = get_name_map(dir_contents)

def get_show(show_name):
    query_url = show_search_url.format(urllib.parse.quote(show_name))
    with urllib.request.urlopen(query_url) as response:
        json_data = json.loads(response.readall().decode('utf-8'))
    return json_data['id'], json_data['name'], json_data['summary']


def test():
    print(get_show(show_name))

if __name__ == "__main__":
    test()
