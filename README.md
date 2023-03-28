# Broadway Musical Lyrics Analysis
This project aims to analyze the impact of a musical's lyrics on its Broadway attendance and represent this data in a plot.

For our implementation, a shows' total attendance across its run on Broadway is compared to the uniqueness of its lyrics, with uniqueness being defined as an average of the number of unique words vs the number of total words in each song.

Combining data from the [CORGIS (Collection of Really Great, Intersting, Situated Datasets) Project](https://corgis-edu.github.io/corgis/) Broadway dataset with lyrical data from the website [Genius](https://genius.com) and the [LyricsGenius Python Library](lyricsgenius.readthedocs.io/), comparisons can be made between lyric composition and the performance of a show. 

## Setup Requirements
In order to run this code:
* Clone the repo from GitHub to your computer.
* Install the nessesary libraries (lyricsgenius, pandas, requests) by running `pip install -r requirements.txt` from the command line.
* Rename the api_keys.py.example file to api_keys.py, and replace the value of `CLIENT_ACCESS_TOKEN` with a token requested from the [Genius Developer Portal](https://genius.com/api-clients).
* Create an empty directory titled `lyrics` in the project root directory, if one does not already exist.

## Code Hierarchy
* `broadway_data.py` contains code to download the CORGIS Broadway Dataset (or optionally, a different dataset in the same format) and complete various processing steps on it. This includes removing columns not being used for a particular implementation (controlled by the `COLUMNS_TO_REMOVE` list) and summing the performance data of all showings of a musical (as each musical is reported on a week-by-week basis). Data is writen to the `processed_broadway_data.csv` and `summed_broadway_data.csv` at their respective stages of the project.
* `genius_lyrics.py` provides various functions for interfacing with Genius to acquire lyrics. It provides code to first match a musical with its recording album and then download each song from the musical's lyrics. Lyrics are written to a CSV file in the aforementioned lyrics folder to reduce the need to continually request them from the Genius API (which is a slow, slow process.)
* `compile_data.py` implements the functions to match albums and download lyrics in `genius_lyrics` with the processed data from the Broadway dataset.

## Reproducing Results
`compile_data.py` provides an overview of how all of the various pieces of this project come together to analyze lyrical data, and we suggest you take a look at this if you're looking to do a similar analysis of lyrics.

For a more complete look at our implementation and results, more information can be found in the project's [computational essay](https://writings.stephenwolfram.com/2017/11/what-is-a-computational-essay/). This essay is provided in the format of a Jupyter iteractive Python notebook (.ipynb) file, formatted with Quarto for easier version control. This can be viewed by
* Installing quarto with `pip install quarto`
* Converting the essay by running `quarto convert lyrical_analysis_essay.qmd`
* Opening the converted notebook (`lyrical_analysis_essay.ipynb`) either using the Jupyter editor, VS Code Jupyter plugin, or another tool capable of reading these files.

