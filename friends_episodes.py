from epnamer import *

# Loads over the top of the current file!
guide = tvmaze_guide('Friends')
friends = list(guide)
with open('friends_episodes.py', 'w') as f:
    f.write('from epnamer import Episode\n')
    f.write('friends = [\n')
    for episode in friends:
        f.write(str(episode) + ',\n')
    f.write(']\n')

