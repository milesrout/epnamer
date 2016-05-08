from collections import namedtuple
import json
import os
import re
import sys
import urllib.request

Episode = namedtuple('Episode', 'show, s, e, title')
Video = namedtuple('Video', 'filename, s, e, suffix')

def _json_query(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.readall().decode('utf-8'))


class tvmaze_guide:
    def __init__(self, *args):
        self.episodes = []
        self.show = None
        if args:
            self.fetch(*args)

    def __iter__(self):
        yield from self.episodes

    def _find_show_id(self, show_name):
        url = 'http://api.tvmaze.com/singlesearch/shows?q={}'
        print("Getting show data from TVmaze <tvmaze.com> ...")
        query = url.format(urllib.parse.quote(show_name))
        result = _json_query(query)
        self.show = result['name']
        print("Show data found at", result['url'])
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


def epcode_res():
    re_strs = [r'S(\d\d)E(\d\d)', r'Season (\d+) Episode (\d+)']
    return list(re.compile(s, re.IGNORECASE) for s in re_strs)


def parse_video(filename, season, num):
    tags = ['360p', '480p','720p', '1080p', 'x264', 'x265']
    suffix = ''.join(tag for tag in tags if tag in filename.split('/')[-1])
    return Video(filename, season, num, suffix)


def iter_videos(filenames):
    for filename in filenames:
        for epcode_re in epcode_res():
            match = epcode_re.search(os.path.basename(filename))
            if match:
                yield parse_video(filename, *map(int, match.groups()))

def make_name(video, episode):
    text_strip = lambda s: ''.join(c for c in s if c.isalnum() or c == ' ')
    text_map = lambda s: text_strip(s).replace(' ', '.')
    file_format = '{}.S{:02}E{:02}.{}'
    suffix = '.' + video.suffix if video.suffix else ''
    extension = os.path.splitext(video.filename)[1]
    return file_format.format(text_map(episode.show), episode.s, episode.e,
            text_map(episode.title)) + suffix + extension

def _iter_rename_table(filenames, guide):
    videos = list(iter_videos(filenames))
    for video in iter_videos(filenames):
        for episode in guide:
            if (episode.s, episode.e) == (video.s, video.e):
                yield video.filename, make_name(video, episode)
                break

def rename_map(filenames, guide):
    return {k: v for k, v in _iter_rename_table(filenames, guide)}

def recursive_iter_paths(targets):
    for target in targets:
        if os.path.isdir(target):
            dir_contents = (os.path.join(target, t) for t in os.listdir(target))
            yield from recursive_iter_paths(dir_contents)
        elif os.path.exists(target):
            yield target

def print_usage():
    print("Usage: {} SHOWNAME FILE...")

def main():
    if len(sys.argv) < 3:
        print_usage()
        sys.exit()

    try:
        guide = tvmaze_guide(sys.argv[1])
    except urllib.error.HTTPError:
        guide = None
    if not guide:
        print("Could not find show", sys.argv[1], "in database.")
        sys.exit(1)

    filenames = list(recursive_iter_paths(sys.argv[2:]))
    if not filenames:
        print("No files to rename.")
        sys.exit(1)

    print(rename_map(filenames, guide))


if __name__ == '__main__':
    main()
