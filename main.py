from utils.helpers import save_lyrics
from config import AUDIO_EXTENSIONS, MUSIC_DIRECTORY, OUTPUT_DIRECTORY, LYRICS_FETCH_MODE
from pathlib import Path
import logging
from utils.fetch.from_all import fetch_lyrics

def main() -> int:
    """main function

    :return: 0
    :rtype: int
    """

    log = logging.getLogger(__name__)

    total_processed = 0
    total_found_and_saved = 0

    music_dir = Path(MUSIC_DIRECTORY)
    music_files = (
        f for f in music_dir.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
    )

    for song_path in music_files:
        total_processed += 1
        try:
            log.info(f"{total_processed}. {song_path.stem}")
            lyrics = fetch_lyrics(song_path=song_path, fetch_mode=LYRICS_FETCH_MODE)
            if isinstance(lyrics, str):
                # save lyrics to location
                save_lyrics(lyrics=lyrics, out_dir=OUTPUT_DIRECTORY, out_filename=song_path.stem) # song.stem = song filename only
                total_found_and_saved += 1

        except Exception as e: log.exception(f"FAILED: {song_path.name}")

    log.info("==== Summary ====")
    success_rate = ((total_found_and_saved / total_processed) * 100 if total_processed else 0.0)
    log.info(f"Success Rate: {success_rate:0.2f}% | {total_found_and_saved}/{total_processed}")
    
    return 0

if __name__ == "__main__":
    main()

