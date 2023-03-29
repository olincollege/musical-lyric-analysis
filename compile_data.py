import csv
import matplotlib.pyplot as plt
import pandas as pd
import genius_lyrics as lyrics


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


def find_all_uniqueness_scores():
    """
    Calculates the uniqueness score and total lyric count for every musical and
    writes this data as well as the previous data to a new CSV file.
    """
    with open("musical_genius_data.csv", "r", encoding="utf-8") as file:
        musical_scores = pd.read_csv(file)
    # album_ids will hold the album's Genius ID
    album_ids = musical_scores["GeniusID"]

    # empty lists that will hold each musical's uniqueness score and total lyric
    # count respectively
    uniqueness_scores = []
    lyric_totals = []

    # calculates uniqueness score and total lyric count for each show and then
    # adds them to the lists
    for album_id in album_ids:
        with open(f"lyrics/{album_id}.csv", "r", encoding="utf-8") as read_obj:
            csv_reader = csv.reader(read_obj)
            # convert string to list
            all_lyrics = list(csv_reader)

        score = lyrics.calculate_album_uniqueness(all_lyrics)
        uniqueness_scores.append(score)

        total_lyrics = lyrics.calculate_total_lyrics(lyrics.get_all_lyrics(album_id))
        lyric_totals.append(total_lyrics)

    # makes new columns in the CSV file to store the uniqueness scores and total
    # lyric count
    musical_scores["UniquenessScore"] = uniqueness_scores
    musical_scores["TotalLyricCount"] = lyric_totals

    # writes the new data to a new CSV file
    musical_scores.to_csv("musical_scores.csv", encoding="utf-8", index=False)


def avg_scores_data():
    """
    Calculates the average attendance, number of weeks on broadway, and total
    number of performances for each lyrical uniqueness score and stores this
    data in a new CSV file titled score_dataframe.csv.
    """
    with open("musical_scores.csv", "r", encoding="utf-8") as file:
        musical_scores = pd.read_csv(file)

    # A numpy array of all unique uniqueness scores are pulled from
    # musical_scores.csv and saved to a list for easier looping.
    all_scores = musical_scores["UniquenessScore"].unique().tolist()

    # Each score is added in order of the list to a new pandas dataframe to
    # store only the total information for each score.
    score_dataframe = pd.DataFrame({"UniquenessScore": all_scores})

    # Blank lists are created prior to the following loop to collect the total
    # information for each score. By looping through the list of scores
    # in order and adding them to each list in order, we can be assured that
    # the correct numbers correspond to each score when adding to the
    # dataframe later.
    all_scores_attendance = []
    all_scores_weeks = []
    all_scores_performances = []

    # Each unique score is looped through, where all shows with that score are
    # pulled out of the complete dataframe and then the total attendance,
    # number of weeks on broadway, and total performances are each averaged.
    # These are added to the previously created lists in the same order as the
    # scores.
    for score in all_scores:
        all_same_scores = musical_scores[musical_scores["UniquenessScore"] == score]

        # averaging attendance
        attendance = all_same_scores["Attendance"].mean()
        all_scores_attendance.append(attendance)

        # averaging the total number of weeks on Broadway
        weeks = all_same_scores["WeeksPerformed"].mean()
        all_scores_weeks.append(weeks)

        # averaging number of performances
        performances = all_same_scores["NumPerformances"].mean()
        all_scores_performances.append(performances)

    # Each list is then added as a new column of the newly created dataframe.
    score_dataframe["Attendance"] = all_scores_attendance
    score_dataframe["WeeksPerformed"] = all_scores_weeks
    score_dataframe["NumPerformances"] = all_scores_performances

    # Finally, this data is again written to a separate csv file in the project
    # directory.
    score_dataframe.to_csv("score_dataframe.csv", encoding="utf-8", index=False)


def plot_data_unique_attendance():
    """
    Creates a plot which shows the average attendance for each lyrical uniqueness
    score. The lyrical uniqueness score is along the x-axis and the average
    attendance is along the y-axis.
    """
    # plot average attendance for each unique score

    with open("score_dataframe.csv", "r", encoding="utf-8") as file:
        scores_dataframe = pd.read_csv(file)

    plt.plot(scores_dataframe["UniquenessScore"], scores_dataframe["Attendance"], "bo")
    plt.xlabel("Lyrical Uniqueness Score")
    plt.ylabel("Average Attendance")
    plt.title("Average Attendance for Each Lyrical Uniqueness Score")
    plt.show()


def plot_data_unique_weeks():
    """
    Creates a plot which shows the average number of weeks on broadway for each
    lyrical uniqueness score. The lyrical uniqueness score is along the x-axis
    and the average number of weeks on broadway is along the y-axis.
    """

    with open("score_dataframe.csv", "r", encoding="utf-8") as file:
        scores_dataframe = pd.read_csv(file)

    # plot average number of weeks on broadway for each unique score
    plt.plot(
        scores_dataframe["UniquenessScore"], scores_dataframe["WeeksPerformed"], "bo"
    )
    plt.xlabel("Lyrical Uniqueness Score")
    plt.ylabel("Average Number of Weeks on Broadway")
    plt.title("Average Number of Weeks on Broadway for Each Lyrical Uniqueness Score")
    plt.show()


def plot_data_total_attendance():
    """
    Creates a plot which shows the attendance in comparison to the total number
    of lyrics in a broadway show. The number of lyrics in the show is along the
    x-axis and the attendance is along the y-axis.
    """

    with open("musical_scores.csv", "r", encoding="utf-8") as file:
        musical_scores = pd.read_csv(file)

    # plot attendance compared to total lyric count
    plt.plot(musical_scores["TotalLyricCount"], musical_scores["Attendance"], "bo")
    plt.xlabel("Total Number of Lyrics")
    plt.ylabel("Attendance")
    plt.title("Total Broadway Attendance for Different Number of Total Lyrics")
    plt.show()
