import os
import re

target_dir = "~/epnamer/test"
show_name = "Friends"

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
    dir_contents = os.listdir('test')
    new_names = get_name_map(dir_contents)

if __name__ == "__main__":
    main()
