import time
import random

def human_delay(mean: float = 9.0, jitter: float = 0.3, minimum: float = 5.0):
    delay = random.gauss(mean, mean * jitter)
    time.sleep(max(minimum, delay))

def save_lyrics(lyrics:str, out_dir: str, out_filename:str) -> bool:
    lyrics_file = out_dir + f"\\{out_filename}.lrc"
    with open(lyrics_file, "w", encoding="utf-8") as f:
        f.write(lyrics)
    return True

def extract_spotify_lyrics(json_data: dict) -> str|bool:
    """
    extract spotify lyrics from json response
    
    Args:
        json_data: json response from spotify fetch

    Returns:
        lyrics(str) if found, otherwise False
    """
    if json_data is None:
        return False

    def ms_to_timestamp(ms: int) -> str:
        minutes = ms // 60000
        seconds = (ms % 60000) / 1000
        return f"{minutes:02d}:{seconds:05.2f}"

    lyrics = json_data.get("lyrics", {})
    lines_data = lyrics.get("lines", [])

    lrc_lines = []
    for entry in lines_data:
        words = entry.get("words", "").strip()
        if not words:
            continue

        start_ms = int(entry["startTimeMs"])
        timestamp = ms_to_timestamp(start_ms)
        lrc_lines.append(f"[{timestamp}]{words}")

    return "\n".join(lrc_lines)

def synced_lrclib(json_data:list[dict]) -> str|bool:
    """
    Returns:
        synced lyrics(str) if found, otherwise False
    """
    if not isinstance(json_data, list):
        return False

    for item in json_data:
        synced_lyrics = item.get("syncedLyrics")
        if  synced_lyrics == None:
            pass
        else:
            return synced_lyrics

    return False

def unsynced_lrclib(json_data:list[dict]) -> str|bool:
    """
    Returns:
        unsynced lyrics(str) if found, otherwise False
    """
    if not isinstance(json_data, list):
        return False

    for item in json_data:
        unsynced_lyrics = item.get("plainLyrics")
        if  unsynced_lyrics == None:
            pass
        else:
            return unsynced_lyrics
    return False

def extract_lrclib_lyrics(json_data: list[dict], mode: int = 2) -> str|bool:
    """
    extract lyrics from json data and save to given location

    Args:
        data: json data(response) recieved from api request
        out_dir: output location for lyrics
        out_filename: output file name to be saved as
        mode: synced(0), unsynced(1), synced_with_fallback(2)

    Returns:
        lyrics(str) if found, otherwise False.
    """

    if not json_data:
        return False

    match mode:
        case 0: # synced only
            lyrics = synced_lrclib(json_data=json_data)
            if lyrics: return lyrics
        case 1: # unsynced only
            lyrics = unsynced_lrclib(json_data=json_data)
            if lyrics: return lyrics
        case 2: # synced with fallback to unsynced
            pass
        case _: # DEFAULT: synced with fallback to unsynced
            pass

    return False

