import re


def polish_song_name(performer: str, song_name: str) -> str:
    # Lowercase copy for safe comparison
    lower_song = song_name.lower()
    lower_performer = performer.lower()

    # Remove performer if present (case-insensitive)
    if lower_performer in lower_song:
        pattern = re.compile(re.escape(performer), re.IGNORECASE)
        song_name = pattern.sub("", song_name)

    # Replace common separators
    song_name = song_name.replace("_", " ").replace("-", " ")

    # Remove unwanted suffixes (feat, ft., official, etc.)
    bad_patterns = [
        r"\(.*official.*?\)",  # (Official Video)
        r"\[.*official.*?\]",  # [Official Video]
        r"\(.*lyric.*?\)",  # (Lyric Video)
        r"\[.*lyric.*?\]",
        r"\(.*version.*?\)",  # (Album Version)
        r"\[.*version.*?\]",
        r"\(.*remaster.*?\)",
        r"\[.*remaster.*?\]",
        r"\b(ft\.?|feat\.?)\b.*",  # ft / feat etc.
        r"\bvideo\b.*",
        r"\btopic\b.*",
    ]

    for pat in bad_patterns:
        song_name = re.sub(pat, "", song_name, flags=re.IGNORECASE)

    # Remove multiple spaces
    song_name = re.sub(r"\s+", " ", song_name)

    return song_name.strip()
