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
    # creates empty lists to hold future data
    list_musical_title = []
    list_musical_genius_id = []
    list_album_title = []

    with open("summed_broadway_data.csv", "r", encoding="utf-8") as file:
        musical_data = pd.read_csv(file)

    # adds the show names to the list of musical titles
    list_musical_title.extend(musical_data["ShowName"].tolist())

    # finds the name of the Genius album and the Genius Album ID for each of the
    # shows in the list of musical titles.
    for musical_title in list_musical_title:
        (musical_genius_id, album_title) = lyrics.find_album(musical_title)
        # adds all Genius Album IDs to the album id list
        list_musical_genius_id.append(musical_genius_id)
        # adds all album titles to the album title list
        list_album_title.append(album_title)

    # creates new columns in musical_data to hold the album titles and IDs
    musical_data["GeniusID"] = list_musical_genius_id
    musical_data["AlbumTitle"] = list_album_title
    # removes musicals from the dataset if it's Genius Album can not be found
    musical_data = musical_data[musical_data["GeniusID"] != "-1"]
    # resets the indexes in the dataset
    musical_data = musical_data.reset_index(drop=True)

    # writes the dataset to a new CSV file
    musical_data.to_csv("musical_genius_data.csv", encoding="utf-8", index=False)


def download_lyrics():
    """
    Downloads all lyrics from every listed musical and puts them each in
    separate csv files based on show.
    """
    with open("musical_genius_data.csv", "r", encoding="utf-8") as file:
        musical_data = pd.read_csv(file)

    # album_ids will hold the album's Genius ID
    album_ids = musical_data["GeniusID"]

    # downloads all lyrics from a show to a CSV file
    # repeats this for every show with a Genius ID
    for album_id in album_ids:
        lyrics.get_all_lyrics(album_id)
