import re

SONG_RE_PATTERN = re.compile("(.+) - (.+)")


def extract_artist_and_title(song, regex=SONG_RE_PATTERN):
    """
    We get a single string with both artist and title, which isn't great.
    Try and extract artist and title out of it. It won't necessarily be super
    accurate.
    """
    match = SONG_RE_PATTERN.search(song)
    if match:
        return (match.group(1), match.group(2))
    raise ValueError(f"Could not extract artist and title from text: {song}")
