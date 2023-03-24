import lyricsgenius as lg
import api_keys as key
import csv

LIST_OF_ALBUM_KEYWORDS = ["Broadway", "Cast", "Recording"]

# A list of punctuation marks to ignore when doing lyrical analysis. This is
# copied from Python's built-in string.punctuation, however, the brackets []
# have been removed since anything inside of brackets will be removed entirely
# (the words themselves, not just the marks)
PUNCTUATION_MARKS = "\"!#$%&'()*+,-./:;<=>?@\^_`{|}~"

# List of random sequences that make it into lyrics that, if found, should be
# removed
REMOVE_FROM_LYRICS = ["\u200b", "translations", "embed"]


def find_album(name):
    """
    Using the lyricsgenius library, search for a given musical's album on
    Genius. In order to make sure the lyrics returned are correct, a series of
    keywords is searched for in the album title and artist name. These keywords
    are ones frequently associated with Broadway musical recordings on Genius.
    The first album with the correct keywords is presumed correct and is
    returned. All returns are in the form of a Genius album ID number that can
    later be used to return all tracks from the album.

    Args:
        name: string representing the name of the musical to be searched for.
    Returns:
        A tuple containing:
            String consisting of a numeric album ID for the correctly identified
                album. If no album is found that matches the keyword criteria,
                -1 is returned (as a string).
            String consisting of the name of the album found to be matching.
    """

    genius_object = lg.Genius(key.CLIENT_ACCESS_TOKEN)

    # Some musicals have years in the name that causes issues with Genius
    # results. If the name contains such a year (either in the format 'YY or
    # YYYY at the end of the name), it is removed before the search takes place.
    #
    # This is placed inside a try block to prevent musicals with names
    # shorter than 4 characters from causing an error. If such an error is
    # thrown, the name can't contain a year and the program will continue
    # unchanged.
    try:
        if name[-3] == "'":
            name = name[0 : (len(name) - 4)]
        elif name[len(name) - 2 : len(name)].isnumeric():
            name = name[0 : (len(name) - 3)]
        elif name[(len(name) - 4) : len(name)].isnumeric():
            name = name[0 : (len(name) - 5)]
    except IndexError:
        pass

    # Use the genius object from lyricsgenius to search Genius for an album of
    # the given musical's name. This returns 5 results in a dictionary in
    # JSON-format.
    album_dict = genius_object.search_albums(name)

    # Remove unnecessary JSON nesting sections for the returned results.
    album_dict = album_dict["sections"][0]["hits"]

    # Search each of the result albums for one that contains the defined
    # keywords in either the title or artist name. If one is found, it is
    # immediately returned and the rest of the results are ignored.
    for album in album_dict:
        album_title = album["result"]["full_title"]
        album_artist = album["result"]["artist"]["name"]
        for keyword in LIST_OF_ALBUM_KEYWORDS:
            if (keyword in album_title) or (keyword in album_artist):
                return (album["result"]["id"], album["result"]["full_title"])

    # If no albums with the requested keywords are found, the musical should be
    # ignored in the data as there is no match on Genius. -1 is returned to
    # signify this.
    return ("-1", "Not Found")


def download_all_lyrics(album_id):
    """
    Given an ID of a genius album, get all lyrics of all songs on that album.

    Args:
        album_id: string representing the numerical Genius ID of the album
    Returns:
        A list of lists. Each embedded list contains strings representing each
            individual word in the song.
    """

    genius_object = lg.Genius(key.CLIENT_ACCESS_TOKEN)

    # If the find_album method fails to find a match for an album, it returns
    # -1, so any album IDs equal to -1 should be ignored and an empty string
    # should be returned.
    if album_id == -1:
        return []

    # Get a dictionary representing all of the tracks in an album and their
    # associated data.
    all_tracks = genius_object.album_tracks(album_id)

    # Remove extra dictionary later
    all_tracks = all_tracks["tracks"]

    # Create empty list to store each individual song's list of lyrics
    album_lyrics = []

    # Loop through each song in the album to find lyrics and add to the list of
    # all lyrics.
    for song in all_tracks:

        # The Genius API indicates if a song is all instrumentals, and will
        # throw an error if the lyrics of such a song are requested. If an
        # instrumental song is reached, it is ignored and the loop continues to
        # the next song on the album.
        if song["song"]["instrumental"]:
            continue

        # Pulls the song ID out from the rest of the information provided by the
        # Genius API
        song_id = song["song"]["id"]

        # Uses lyricsgenius to get the lyrics for the requested song based on
        # it's ID
        #
        # _NOTE: The Genius API doesn't provide lyrics directly, so the
        # lyricsgenius library scraped
        song_lyrics = genius_object.lyrics(song_id)

        # This line replaces all punctuation marks in the string with empty
        # space so that words are not marked as unique just because they have
        # punctuation marks in them.
        song_lyrics = song_lyrics.translate(str.maketrans("", "", PUNCTUATION_MARKS))

        # The single string containing all lyrics in the song is split into a
        # list. Without another parameter, the split function will by default
        # split strings based on white space, which will result in each word
        # getting its own individual place in the list.
        song_lyrics_split = song_lyrics.split()

        # Using list comprehension, all words within this list that are touching
        # brackets are removed. Having notes regarding who is singing is common
        # in musicals, however, these notes are not sung and thus shouldn't be
        # included with in the lyrics
        song_lyrics_filtered = [
            word.lower()
            for word in song_lyrics_split
            if (("[" not in word) and ("]" not in word))
        ]

        # The results returned by the lyricsgenius library were found to
        # consistently contain extra garbage with the first and second word.
        # To alleviate this, the only way to reliably handle this is to
        # remove these words completely.
        song_lyrics_filtered = song_lyrics_filtered[1 : len(song_lyrics_filtered) - 1]

        # Each list is appended to the master list for all songs in the album.
        album_lyrics.append(song_lyrics_filtered)

    return album_lyrics


def write_lyrics_to_file(album_id):
    """
    Save a musical's lyrics to a CSV file.

    Since it takes an incredibly long time to search Genius for the lyrics of
    an entire musical, it makes the most sense to complete this process once
    and then save it to a CSV file so it only has to be ran once.

    The CSV file is formatted such that each row represents a song and a one
    word is placed in each column. The album's Genius ID will be used as the
    filename for ease of use.

    Args:
        album_id: string, numerical ID for an album on Genius.
    Returns:
        Nothing.
    """

    lyrics = download_all_lyrics(album_id)

    filepath = f"lyrics/{album_id}.csv"

    with open(filepath, "w", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(lyrics)


def get_all_lyrics(album_id):
    """
    Given an album ID, this function will first try to load the lyrics from a
    file if they are already downloaded. If the album has not already been
    downloaded, it is grabbed from Genius and then loaded from the file
    created.

    Args:
        album_id: string representing the album's numerical Genius ID
    Returns:
        List of lists, which each embedded list containing strings for each
            individual word in a songs lyrics. Each song on the album
            gets its own embedded list.
    """

    file_path = f"lyrics/{album_id}.csv"

    lyrics = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            # Use CSV library to open CSV; create list of lists in the format
            # that we are looking for.
            csv_reader = csv.reader(file)
            lyrics = list(csv_reader)
    except FileNotFoundError:
        write_lyrics_to_file(album_id)
        with open(file_path, "r", encoding="utf-8") as file:
            # Use CSV library to open CSV; create list of lists in the format
            # that we are looking for.
            csv_reader = csv.reader(file)
            lyrics = list(csv_reader)

    return lyrics


def calculate_lyrical_uniqueness(lyrics):
    """ "
    Calculates the lyrical uniqueness of a song. Lyrical uniqueness is defined
    as the percentage of unique words compared to the total number of words in a
    song.

    Args:
        lyrics: list of strings representing all of the individual words in a
            song.
    Returns:
        Integer (rounded) percentage of words that are unique in a song
    """

    unique_words = []

    for word in lyrics:
        if word not in unique_words:
            unique_words.append(word)

    return int((len(unique_words) / len(lyrics)) * 100)


def calculate_album_uniqueness(all_album_lyrics):
    """
    Calculate the average uniqueness of all songs in an album.

    Each song's uniqueness is found individually, and then these values are all
    averaged to find a (rounded, whole number) percent uniqueness of the album's
    lyrics.

    Args:
        all_album_lyrics: list of lists of strings, which each embedded list
            containing each word in the lyrics of one of the album's song as
            individual strings.
    Return:
        Integer representing the percent uniqueness of an album's lyrics, on
            average
    """

    total_percentages = 0

    for song in all_album_lyrics:
        total_percentages += calculate_lyrical_uniqueness(song)

    return int(total_percentages / len(all_album_lyrics))
