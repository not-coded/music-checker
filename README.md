# Music Checker

This tool checks if the song file has the right metadata by:

1. Comparing the YouTube link to the song metadata.
2. If there is no link then it will use the title and artist of the metadata.
3. If the artist or author of the metadata is in the YouTube video then it will mark it as correct.
4. Otherwise it will search for the first result and check whether it matches the title and artist.

The tool also shows the metadata of the song file and the YouTube video.

# Showcase

TODO

## How to use

Check [GitHub Releases](https://github.com/not-coded/music-checker/releases) for a one-click executable (but it's not recommended to use it due to the file size).

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
python music-checker.py
```