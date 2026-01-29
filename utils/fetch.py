

def lyrics(search_query:str, source:list, mode:str="synced_with_fallback") -> str|None:
    """
    Fetch lyrics from given source list.

    Args:
        search_query: Formatted search query string with song title, artist(s), album.
        source: List of sources in order of preference(only - lrclib, musixmatch)
        mode: Type of lyrics to fetch. Allowed values - synced, unsynced, synced_with_fallback

    Returns:
        Lyrics text if found, otherwise None.
    """
    return None

get_lyrics(search_query="", source=[], mode="")
