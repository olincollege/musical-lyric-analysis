import requests
import pandas as pd
import io

BROADWAY_DATA_URL = (
    "https://corgis-edu.github.io/corgis/datasets/csv/broadway/broadway.csv"
)


def get_broadway_data(data_download_url=BROADWAY_DATA_URL):
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
    Returns:
        Nothing. The filtered Broadway cast data is written to a csv file in the
            same directory.
    """
    broadway_data_request = requests.get(BROADWAY_DATA_URL)
    broadway_dataframe = pd.read_csv(io.StringIO(broadway_data_request.text))

    broadway_musicals = broadway_dataframe[broadway_dataframe["Show.Type"] == "Musical"]
    broadway_musicals = broadway_musicals[broadway_musicals["Date.Year"] >= 1995]

    COLUMNS_TO_DROP = [
        "Date.Day",
        "Date.Month",
        "Date.Year",
        "Show.Theatre",
        "Statistics.Capacity",
        "Statistics.Gross",
        "Statistics.Gross Potential",
        "Statistics.Performances",
    ]

    for column in COLUMNS_TO_DROP:
        broadway_musicals.drop(column, axis=1, inplace=True)

    broadway_musicals= broadway_musicals.reset_index(drop=True)
    
    broadway_musicals.to_csv("processed_broadway_data.csv", encoding="utf-8", index=False)
