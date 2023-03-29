"""
Various functions to download and process the CORGIS Broadway dataset.
"""
import io
import requests
import pandas as pd


BROADWAY_DATA_URL = (
    "https://corgis-edu.github.io/corgis/datasets/csv/broadway/broadway.csv"
)

PROCESSED_FILE_PATH = "processed_broadway_data.csv"
SUMMED_FILE_PATH = "summed_broadway_data.csv"

# define a list of columns that is included in the original CORGIS dataset
# that are not useful to our project and thus can be dropped. Drop each
# column in the list from the dataframe.
COLUMNS_TO_DROP = [
    "Date.Day",
    "Date.Month",
    "Date.Year",
    "Show.Theatre",
    "Statistics.Capacity",
    "Statistics.Gross",
    "Statistics.Gross Potential",
]


def get_broadway_data(
    data_download_url=BROADWAY_DATA_URL, filepath=PROCESSED_FILE_PATH
):
    """
    Download Broadway data from the CORGIS database and filter it.

    Any data earlier than 1995 is filtered out since it is incomplete
    and could skew data. Only musicals are taken out of the dataset (ignoring
    plays, which are also in the original data). Finally, only attendance is
    recorded and other metrics are discarded.

    Args:
        data_download_url: string that represents a URL to download a CSV file
            representing broadway data. This defaults to the URL to the CORGIS
            Broadway dataset. Alternatively, a different URL can be provided.
        filepath: string representing the filepath to save the resultant csv
            file to in relation to the project directory. Defaults to a standard
            value, processed_broadway_data.csv
    Returns:
        Nothing. The filtered Broadway cast data is written to a csv file in the
            same directory.
    """

    # Download the provided CSV files, and turn them into a pandas dataframe
    broadway_data_request = requests.get(data_download_url)
    broadway_dataframe = pd.read_csv(io.StringIO(broadway_data_request.text))

    # remove any show that is not a musical (outside the scope of this project),
    # and remove any show before 1995, as data before this time is incomplete.
    broadway_musicals = broadway_dataframe[
        broadway_dataframe["Show.Type"] == "Musical"
    ]
    broadway_musicals = broadway_musicals[
        broadway_musicals["Date.Year"] >= 1995
    ]

    for column in COLUMNS_TO_DROP:
        broadway_musicals.drop(column, axis=1, inplace=True)

    # After removing the non-musical performances and performances before 1995,
    # the dataframe indexes do not automatically get reset so that they count up
    # as it included gaps where the removed data was. Resetting indexes
    # renumbers each row to count up form 0.
    broadway_musicals = broadway_musicals.reset_index(drop=True)

    # The new data is written to a CSV file in the project directory. Specifying
    # that index=False ensures that the column titles are assigned correctly
    # and numerical indexes are not redundantly included within the data.
    broadway_musicals.to_csv(filepath, encoding="utf-8", index=False)


def sum_data(load_filepath=PROCESSED_FILE_PATH, save_filepath=SUMMED_FILE_PATH):
    """
    Previous downloaded & filtered Broadway data is loaded from the created csv
    file and the data is further processed to sum all unique musicals
    attendance, number of performances, and length of run together.

    Args:
        filepath - string representing the path to the downloaded and filtered
            broadway dataset in reference to the project folder. Defaults
            to the default name of the processed file path.
    Returns:
        Nothing. A new csv file is written with summed attendance information.
    """

    # Open the previously created and filtered CSV data and put it into a
    # dataframe.
    #
    # To account for error-handling, if the broadway data with the requested
    # filename is not found, the function to download it is automatically called
    # with the given file name.
    try:
        with open(load_filepath, "r", encoding="utf-8") as file:
            processed_dataframe = pd.read_csv(file)
    except FileNotFoundError:
        get_broadway_data(filepath=load_filepath)
        with open(load_filepath, "r", encoding="utf-8") as file:
            processed_dataframe = pd.read_csv(file)

    # A numpy array of all unique show names is pulled from the processed data
    # and saved to a list for easier looping.
    all_musicals = processed_dataframe["Show.Name"].unique().tolist()

    # Each musical is added in order of the list to a new pandas dataframe to
    # store only the total information for each musical.
    summed_dataframe = pd.DataFrame({"ShowName": all_musicals})

    # Blank lists are created prior to the following loop to collect the total
    # information from each musical. By looping through the list of musicals
    # in order and adding them to each list in order, we can be assured that
    # the correct numbers correspond to each musical when adding to the
    # dataframe later.
    all_musicals_attendance = []
    all_musicals_num_performances = []
    all_musicals_length_of_run = []

    # each unique musical is looped through, where all performances of that
    # musical are pulled out of the complete dataframe and then the total
    # attendance and number of performances are summed together. These are added
    # to the prior created lists in the same order as the musicals.
    # The number of weeks the musical was on broadway is also calculated based
    # on the number of entries.
    for musical in all_musicals:
        all_performances_of_musical = processed_dataframe[
            processed_dataframe["Show.Name"] == musical
        ]

        all_performances_of_musical = all_performances_of_musical.reset_index(
            drop=True
        )

        all_musicals_length_of_run.append(all_performances_of_musical.shape[0])

        attendance = int(
            all_performances_of_musical["Statistics.Attendance"].sum()
        )
        all_musicals_attendance.append(attendance)

        num_performances = int(
            all_performances_of_musical["Statistics.Performances"].sum()
        )
        all_musicals_num_performances.append(num_performances)

    # Each list is then added as a new column of the newly created dataframe.
    summed_dataframe["Attendance"] = all_musicals_attendance
    summed_dataframe["NumPerformances"] = all_musicals_num_performances
    summed_dataframe["WeeksPerformed"] = all_musicals_length_of_run

    # Finally, this data is again written to a separate csv file in the project
    # directory.
    summed_dataframe.to_csv(save_filepath, encoding="utf-8", index=False)
