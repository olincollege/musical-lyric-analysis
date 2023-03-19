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
    album_dict = genius_object.search_albums(name)

    album_dict = album_dict["sections"][0]["hits"]

    for album in album_dict:
        album_title = album["result"]["full_title"]
        album_artist = album["result"]["artist"]["name"]
        for keyword in LIST_OF_ALBUM_KEYWORDS:
            if (keyword in album_title) or (keyword in album_artist):
                return album["result"]["id"]
    
    return "-1"
        

    # current_album_tracks = genius_object.album_tracks(album["result"]["id"])

    
