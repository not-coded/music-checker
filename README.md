# Music Checker

This tool checks if the song file is the right one by:

1. Comparing the YouTube link to the song metadata.
2. If there is no link then it will use the title and artist of the metadata.
3. If the artist or author of the metadata is in the YouTube video then it will mark it as correct.
4. Otherwise it will search for the first 2 results and check which one matches the title and artist the best.

The tool also shows the metadata of the song file and the YouTube video.

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
