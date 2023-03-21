import genius_lyrics as lyrics

def find_corresponding_album(broadway_data_path="summed_broadway_data.csv"):
    """
    Find the lyrical uniqueness of all songs in the Broadway data set.

    Previously calculated Broadway data is loaded, and each unique musical's
    corresponding album is found on Genius. The Genius album ID and album name
    are added to the dataframe. If a match is not able to be identified for a
    musical, then it is removed from the dataset.
    """