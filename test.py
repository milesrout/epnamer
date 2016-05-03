from epnamer import *
from friends_episodes import friends

def seinfeld_episodes():
    print("Seinfeld episodes")
    guide = tvmaze_guide('Seinfeld')
    episodes = list(guide.episodes)
    assert(len(episodes) == 180)
    assert(episodes[0] == Episode(1, 1, 'Good News, Bad News'))


def epcodes():
    print("Epcodes")
    filenames = [
        "Test.S01E12.mkv",
        ".S01E01.dir/foo.avi",
        "Bar Season 1 Episode 18.mp4",
    ]
    print(list(iter_videos(filenames)))


print("Testing:")
seinfeld_episodes()
epcodes()


