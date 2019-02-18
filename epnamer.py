from collections import namedtuple
import json
import os
import re
import sys
import urllib.request


season_num = None
Episode = namedtuple('Episode', 'show, s, e, title')
Video = namedtuple('Video', 'filepath, s, e, suffix')


default_epcode_res = list(re.compile(s, re.IGNORECASE) for s in [
    r'S(\d\d)E(\d\d)',
    r'Season (\d+) Episode (\d+)',
    r'\s(\d)x(\d\d)\s',
    r'\s(\d)(\d\d)\s',
])


def _json_query(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode('utf-8'))


class tvmaze_guide:
    def __init__(self, *args):
        self.episodes = []
        self.show = None
        if args:
            self.fetch(*args)

    def api_source(self):
        return 'TVmaze <tvmaze.com>'

    def __iter__(self):
        yield from self.episodes

    def _find_show_id(self, show_name):
        url = 'http://api.tvmaze.com/singlesearch/shows?q={}'
        query = url.format(urllib.parse.quote(show_name))
        result = _json_query(query)
        self.show = result['name']
        return result['id']

    def _parse_episode(self, ep_data):
        return Episode(
                self.show,
                ep_data['season'],
                ep_data['number'],
                ep_data['name'])

    def fetch(self, show_name):
        show_id = self._find_show_id(show_name)
        url = 'http://api.tvmaze.com/shows/{}/episodes'
        query = url.format(show_id)
        result = _json_query(query)
        for ep_result in result:
            self.episodes.append(self._parse_episode(ep_result))


def parse_video(filepath, season, num):
    tags = ['360p', '480p','720p', '1080p', 'x264', 'x265']
    filename = os.path.basename(filepath)
    suffix = '.'.join(tag for tag in tags if tag in filename)
    return Video(filepath, season, num, suffix)


def iter_videos(filepaths, epcode_res):
    for filepath in filepaths:
        for epcode_re in epcode_res:
            match = epcode_re.search(os.path.basename(filepath))
            if match:
                if season_num is not None:
                    yield parse_video(filepath, season_num, *map(int, match.groups()))
                else:
                    yield parse_video(filepath, *map(int, match.groups()))

def make_name(video, episode):
    strip_text = lambda s: ''.join(c for c in s if c.isalnum() or c in ' &')
    sanitize_text = lambda s: strip_text(s).replace(' ', '.')
    file_format = '{}.S{:02}E{:02}.{}{}{}'
    suffix = '.' + video.suffix if video.suffix else ''
    extension = os.path.splitext(video.filepath)[1]
    return file_format.format(sanitize_text(episode.show), episode.s,
            episode.e, sanitize_text(episode.title), suffix, extension)

def _iter_rename_table(filepaths, guide, epcode_res):
    videos = list(iter_videos(filepaths, epcode_res))
    for video in videos:
        for episode in guide:
            if (episode.s, episode.e) == (video.s, video.e):
                new_name = make_name(video, episode)
                directory = os.path.dirname(video.filepath)
                new_path = os.path.join(directory, new_name)
                yield video.filepath, new_path
                break

def get_rename_map(filepaths, guide, epcode_res):
    return {k: v for k, v in _iter_rename_table(filepaths, guide, epcode_res)}

def recursive_iter_paths(targets):
    for target in targets:
        if os.path.isdir(target):
            dir_contents = (os.path.join(target, t) for t in os.listdir(target))
            yield from recursive_iter_paths(dir_contents)
        elif os.path.exists(target):
            yield target

def do_renaming(rename_map, undo_file=None):
    if os.name == 'nt':
        move_cmd = 'move'
    else:
        move_cmd = 'mv'
    for filepath in rename_map:
        escaped_dest = rename_map[filepath].replace('"', '\\"')
        escaped_src = filepath.replace('"', '\\"')
        if undo_file:
            undo_file.write('{} '.format(move_cmd))
            undo_file.write('"{}" "{}"\n'.format(escaped_dest, escaped_src))
        os.rename(filepath, rename_map[filepath])

def main():
    if len(sys.argv) < 3:
        print("Usage: {} [-e REGEX] [-s SEASON] SHOWNAME FILE...")
        print("\tREGEX must match a season and episode, eg", r'S(\d\d)E(\d\d)')
        print("\tunless the SEASON is provided, in which case it must match just an episode")
        sys.exit()

    global season_num

    arg_pos = 1
    epcode_res = default_epcode_res
    season_num = None

    while sys.argv[arg_pos] in ['-e', '-s']:
        if sys.argv[arg_pos] == '-s':
            season_num = int(sys.argv[arg_pos + 1])
            arg_pos += 2

        if sys.argv[arg_pos] == '-e':
            epcode_res = [re.compile(sys.argv[arg_pos + 1], re.IGNORECASE)]
            arg_pos += 2


    print("Episode guide:", tvmaze_guide().api_source())
    try:
        guide = tvmaze_guide(sys.argv[arg_pos])
    except urllib.error.HTTPError:
        guide = None
    if not guide:
        print("Could not find show", sys.argv[arg_pos], "in database.")
        sys.exit(1)
    arg_pos += 1


    arg_filepaths = list(recursive_iter_paths(sys.argv[arg_pos:]))
    if not arg_filepaths:
        print("No files to rename.")
        sys.exit(1)


    rename_map = get_rename_map(arg_filepaths, guide, epcode_res)


    print("Performing the following renames:")
    printable_map = {f: os.path.basename(rename_map[f]) for f in rename_map}
    for basename in sorted(printable_map):
        print("{} => {}".format(basename, printable_map[basename]))
    print("")
    confirm = input("Continue? [Y/n] ").lower() in ('', 'y', 'yes')
    if not confirm:
        print("Aborted.")
        sys.exit()

    if os.name == 'nt':
        undo_name = 'epnamer-undo.bat'
    else:
        undo_name = 'epnamer-undo.sh'
    with open(undo_name, 'w') as undo_file:
        do_renaming(rename_map, undo_file)




if __name__ == '__main__':
    main()
