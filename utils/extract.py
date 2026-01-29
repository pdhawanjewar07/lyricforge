import json
from pathlib import Path

def extract_and_save(data: str, output_dir: str, mode: int = 0) -> int:
    """
    extract lyrics from json data and save to given location

    Args:
        data: json data(response) recieved from api request
        output_dir: location to save lyrics at
        mode: synced(0), unsynced(1), synced_with_fallback(2)

    Returns:
        0
    """

    json_path = Path(data)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load JSON from file
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    for item in json_data:
        if not isinstance(item, dict):
            continue  # skip garbage

        value = item.get("syncedLyrics")

        if value is None:
            continue  # key missing or null

        lyrics_file = output_dir / "lyrics.lrc"

        with open(lyrics_file, "w", encoding="utf-8") as f:
            f.write(value)

        # stop after first valid lyrics
        break

    return 0


extract_and_save(
    data="C:\\Users\\Max\\Desktop\\VS-Code\\Github Repositories\\time-synced-lyrics\\response0.json",
    output_dir="C:\\Users\\Max\\Desktop\\VS-Code\\Github Repositories\\time-synced-lyrics\\lyrics",
    mode=0,
)
