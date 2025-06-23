# Music Checker

This tool checks if the music file is the right one by:

1. Comparing the YouTube link to the song metadata
    a. If there is no link then it will use the title and artist of the metadata.
2. If the artist or author of the metadata is in the YouTube video then it will mark it as correct.
    a. Otherwise it will search for the first 2 results and check which one matches the title and artist the best.

The tool also shows the metadata of the music file and the YouTube video.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python music-checker.py
```


# Showcase

TODO
