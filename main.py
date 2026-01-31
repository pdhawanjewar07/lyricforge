from utils import build, clean, fetch
from utils.helpers import save_lyrics
from pathlib import Path
from utils.config import AUDIO_EXTENSIONS, MUSIC_DIRECTORY, OUTPUT_DIRECTORY
import os

def main(music_dir:str, out_dir:str) -> int:
    """
    main function

    Args:
        music_dir: music source directory
        out_dir: output directory for lyrics

    Returns:
        0
    """
    total_processed = 0
    total_found_and_saved = 0

    music_dir = Path(music_dir)
    music_files = [f for f in music_dir.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS]
    for song in music_files:
        # print(song.stem) # just song filename
        # """
        total_processed += 1
        print(f"{total_processed}. {song.stem}")

        # build raw search query
        query = build.raw_search_query(song_path=str(song), source=0)

        # clean query
        query = clean.search_query(query=query)
        print(f"Query: {query}")

        # fetch lyrics from musixmatch-via-spotify
        lyrics = fetch.lyrics_musixmatch_via_spotify(search_query=query)

        # fetch lyrics from lrclib
        # lyrics = fetch.lyrics_lrclib(search_query=query)

        # extract and save lyrics to location
        if lyrics:
            save_lyrics(lyrics=lyrics, out_dir=OUTPUT_DIRECTORY, out_filename=song.stem)
            total_found_and_saved += 1
            print("SUCCESS - found")
        else: print("FAILED - not found")

    print(f"\nSuccess Rate: {(total_found_and_saved/total_processed)*100}% | {total_found_and_saved}/{total_processed}")
    # """
    return 0


main(music_dir=MUSIC_DIRECTORY, out_dir=OUTPUT_DIRECTORY)

