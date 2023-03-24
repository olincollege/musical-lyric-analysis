import genius_lyrics as lyrics
import pandas as pd


def find_corresponding_album():
    """
    Find the lyrical uniqueness of all songs in the Broadway data set.

    Previously calculated Broadway data is loaded, and each unique musical's
    corresponding album is found on Genius. The Genius album ID and album name
    are added to the dataframe. If a match is not able to be identified for a
    musical, then it is removed from the dataset.
    """
    list_musical_title = []
    list_musical_genius_id = []
    list_album_title = []

    with open("summed_broadway_data.csv", "r", encoding="utf-8") as file:
        musical_data = pd.read_csv(file)

    list_musical_title.extend(musical_data["ShowName"].tolist())

    for musical_title in list_musical_title:
        (musical_genius_id, album_title) = lyrics.find_album(musical_title)
        list_musical_genius_id.append(musical_genius_id)
        list_album_title.append(album_title)

    musical_data["GeniusID"] = list_musical_genius_id
    musical_data["AlbumTitle"] = list_album_title
    musical_data = musical_data[musical_data["GeniusID"] != "-1"]
    musical_data = musical_data.reset_index(drop=True)

    musical_data.to_csv("musical_genius_data.csv", encoding="utf-8", index=False)
