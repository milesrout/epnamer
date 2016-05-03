from epnamer import *

def seinfeld_episodes():
    print("Seinfeld episodes")
    guide = tvmaze_guide('Seinfeld')
    episodes = list(guide.episodes)
    assert(len(episodes) == 180)
    assert(episodes[0] == Episode(1, 1, 'Good News, Bad News'))

print("Testing:")
seinfeld_episodes()

