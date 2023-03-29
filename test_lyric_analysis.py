import pandas as pd
import pytest
import os
import csv
import genius_lyrics as lyrics
import broadway_data as broadway


#
#
# Tests for genius_lyrics.py
#
# This includes lyrics being correctly processed and uniqueness scores being
# correctly formatted.
#


def test_correct_uniqueness_single_song():
    """
    Test that for a single song, the uniqueness score is equal to the
    number of unique words (each word in the show without duplicates) compared
    to all words in the song (including duplicates of each unique word).

    This list has 2 different words, and a total of 4 words, so the uniqueness
    score should be 50%, or a return of 50.
    """

    lyrics_list = ["one", "two", "two", "two"]

    assert lyrics.calculate_lyrical_uniqueness(lyrics_list) == 50


def test_uniqueness_empty_song():
    """
    Tests that the function to calculate lyrical uniqueness is able to correctly
    handle a song with no lyrics (which happens occasionally due to funky data
    within Genius) by returning a score of zero.
    """

    lyrics_list = []

    assert lyrics.calculate_lyrical_uniqueness(lyrics_list) == 0


def test_uniqueness_no_songs():
    """ "
    Test for an entire album the uniqueness score is correctly calculated for an
    album with no songs with lyrics. This is important to test since Genius
    can sometimes return incomplete data if an album's lyrics have not been
    transcribed.
    """

    song1_lyrics = []

    album_lyrics = [song1_lyrics]

    assert lyrics.calculate_album_uniqueness(album_lyrics) == 0


def test_uniqueness_album_with_one_song():
    """ "
    Test for an entire album the uniqueness score is correctly calculated for an
    album with one song with lyrics.
    """

    song1_lyrics = ["one", "two", "two", "two"]

    album_lyrics = [song1_lyrics]

    assert lyrics.calculate_album_uniqueness(album_lyrics) == 50


def test_uniqueness_full_album():
    """ "
    Test for an entire album the uniqueness score is correctly calculated for an
    album with multiple songs with lyrics.

    song1 is 50% unique, song2 is 75% unique, and the average of these to should
    be 62.5% rounded down to 62%.
    """

    song1_lyrics = ["one", "two", "two", "two"]
    song2_lyrics = ["one", "two", "three", "three"]

    album_lyrics = [song1_lyrics, song2_lyrics]

    assert lyrics.calculate_album_uniqueness(album_lyrics) == 62


def test_standard_lyrics_processed():
    """
    This test makes sure that a "standard" set of lyrics is returned all
    lowercase, words split into a list, and punctuation marks removed.
    Additionally makes sure the first and last word of the lyrics are removed.
    """

    raw_lyrics = "Hello world! Here, is! a standard set's of lyrics."
    expected_result = [
        "world",
        "here",
        "is",
        "a",
        "standard",
        "sets",
        "of",
    ]

    assert lyrics.split_and_format_song_lyrics(raw_lyrics) == expected_result


def test_song_processing_without_lyrics():
    """
    Test that for songs where there are no lyrics, an empty list is returned.
    This could ocassionaly occur for songs that are instrumental but not
    marked as so in the Genius database.
    """

    assert lyrics.split_and_format_song_lyrics("") == []


def test_song_processing_without_genius_matches():
    """ "
    If for whatever reason a song is not found when doing a Genius search for
    it, None is returned. This should result in an empty list so that the song
    is ignored in any following code.
    """

    assert lyrics.split_and_format_song_lyrics(None) == []


def test_words_in_brackets_removed_from_lyrics():
    """
    Test that words contained within brackets are correctly removed. These are
    words that denote which character is speaking and should not be included
    for lyrical analysis as the audience doesn't hear them.
    """

    raw_lyrics = "One two [bracket] three four [bracket bracket] five"
    processed_lyrics = ["two", "three", "four"]

    assert lyrics.split_and_format_song_lyrics(raw_lyrics) == processed_lyrics

def test_lyrics_with_one_word():
    """
    Given the nessesity to manipulate lyrics and remove certain ones,
    check that an error isn't thrown when a song with only one word is
    processed. 
    """

    assert lyrics.split_and_format_song_lyrics("word") == []


#
# Tests for broadway_data.py
#
# This includes ensuring data is downloaded, processed, and summed correctly
#
#

COLUMNS_TO_DROP = [
    "Date.Day",
    "Date.Month",
    "Date.Year",
    "Show.Theatre",
    "Statistics.Capacity",
    "Statistics.Gross",
    "Statistics.Gross Potential",
]

COLUMNS_TO_KEEP = [
    "Show.Name",
    "Statistics.Performances",
    "Statistics.Attendance",
    "Show.Type",
    "Show.Name",
    "Date.Full",
]


def test_downloaded_data_columns():
    """
    Assert that the wanted columns are written to the Broadway data CSV file
    while unwanted columns are removed.

    Both sets of columns based on the CORGIS dataset are included in lists
    defined above this function.

    This function works based on the principle that a data frame will throw a
    KeyError if a column that doesn't exist is referenced, and return the column
    if it does not. We are not testing for values with this test, but rather
    whether or not a KeyError is thrown upon access.

    Aside from checking the correct data is present, this function only pulls
    data from the internet, so no other tests are viable.
    """

    # Create a copy of the CORGIS broadway data with its own filename for
    # this test, and load as a data frame.
    broadway.get_broadway_data(filepath="data_validation.csv")

    with open("data_validation.csv", "r", encoding="utf-8") as file:
        testing_data_frame = pd.read_csv(file)

    # Assert that columns that shouldn't be included result in a KeyError
    for column in COLUMNS_TO_DROP:
        with pytest.raises(KeyError):
            _ = testing_data_frame[column]

    # Assert that columns should exist are loaded without throwing an error.
    # An assert is not included since the value is not being tested, rather
    # that the statement executes without error.
    for column in COLUMNS_TO_KEEP:
        _ = testing_data_frame[column]

    # os.remove deletes the .csv file created for this test to reduce garbage in
    # the directory.
    os.remove("data_validation.csv")


def test_summing_broadway_data():
    """
    Test that data for two Broadway shows as created by the get_broadway_data
    function is correctly summed to reflect all shows by the sum_data function.

    This function should sum the number of performances and attendance for
    all shows across the week. A processed data sample file is loaded and is
    compared against a copy of what should result in this test.

    The testfile includes both musicals with multiple showings and musicals
    with only one show, which should encompass the range of possible occurrences
    for summing data.
    """

    broadway.sum_data(
        "testing/processed_testing_data.csv", "testing/summed_test_data.csv"
    )

    with open("testing/summed_test_data.csv", "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        test_data = list(csv_reader)

    data_key = [
        ["ShowName", "Attendance", "NumPerformances", "WeeksPerformed"],
        ["FWOP's Amazing Performance 1", "145009", "14", "3"],
        ["FWOP's Amazing Performance 2", "13943", "9", "1"],
    ]

    assert test_data == data_key
