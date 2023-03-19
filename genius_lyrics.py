# import lyricsgenius as lg
# import api_keys as key

LIST_OF_ALBUM_KEYWORDS = [
    "Broadway",
    "Cast"
    "Recording"
]

def find_album(name, genius_object):
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
        genius_object: previous instantiated lyricsgenius Genius object with
            defined API key.
    Returns:
        String consisting of a numeric album ID for the correctly identified
            album. If no album is found that matches the keyword criteria, -1
            is returned (as a string).
    """

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
            name = name[0:(len(name) - 4)]
        elif name[(len(name) - 4):len(name)].isnumeric():
            name = name[0:(len(name) - 5)]
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
                return album["result"]["id"]
    
    # If no albums with the requested keywords are found, the musical should be
    # ignored in the data as there is no match on Genius. -1 is returned to
    # signify this.
    return "-1"
        

    # current_album_tracks = genius_object.album_tracks(album["result"]["id"])

    
