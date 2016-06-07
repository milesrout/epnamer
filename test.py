from epnamer import *

def seinfeld_episodes():
    print('Seinfeld episodes')
    guide = tvmaze_guide('Seinfeld')
    episodes = list(guide.episodes)
    assert(len(episodes) == 180)
    assert(episodes[0] == Episode('Seinfeld', 1, 1, 'Good News, Bad News'))


def epcodes():
    print('Epcodes')
    filenames = [
        'Test.S01E12.720p-x264.mkv',
        '.S01E01.dir/foo.avi',
        'Bar Season 1 Episode 18.mp4',
        'Thing 2x05 (HQ).srt',
        'Season 4/Baz 409 The Naming.avi'
    ]
    assert(list(iter_videos(filenames)) == [
        Video('Test.S01E12.720p-x264.mkv', 1, 12, '720p.x264'),
        Video('Bar Season 1 Episode 18.mp4', 1, 18, ''),
        Video('Thing 2x05 (HQ).srt', 2, 5, ''),
        Video('Season 4/Baz 409 The Naming.avi', 4, 9, ''),
    ])

def renaming():
    print('Renaming')
    guide = tvmaze_guide('Seinfeld')
    filenames = [
        'Seinfeld s02e07 720p.mkv',
        's04e11/seinfeld.s02e11.avi',
    ]
    expected = {
        'Seinfeld s02e07 720p.mkv': 'Seinfeld.S02E07.The.Revenge.720p.mkv',
        's04e11/seinfeld.s02e11.avi':
            's04e11/Seinfeld.S02E11.The.Chinese.Restaurant.avi',
    }
    assert(get_rename_map(filenames, guide) == expected)


print('Testing:')
seinfeld_episodes()
epcodes()
renaming()

