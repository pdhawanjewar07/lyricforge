from utils.fetch import lrclib, genius, musixmatch
from utils.helpers import save_lyrics
from pathlib import Path
from utils.config import AUDIO_EXTENSIONS, MUSIC_DIRECTORY, OUTPUT_DIRECTORY

def main(mode:int, music_dir:str, out_dir:str) -> int:
    """
    main function

    Args:
        mode: synced[0], unsynced[1], synced_with_fallback[2]
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
        
        total_processed += 1
        print(f"{total_processed}. {song}")

        # fetch lyrics from musixmatch-via-spotify
        lyrics = musixmatch.fetch_lyrics(song_path=song, mode=mode)

        # fetch lyrics from lrclib
        # lyrics = lrclib.fetch_lyrics(song_path=song, mode=mode)

        # fetch lyrics from genius
        # lyrics = genius.fetch_lyrics(song_path=song)


        # extract and save lyrics to location
        if lyrics:
            save_lyrics(lyrics=lyrics, out_dir=OUTPUT_DIRECTORY, out_filename=song.stem)
            total_found_and_saved += 1
            print("SUCCESS - found")
        else: print("FAILED - not found")

    print(f"\nSuccess Rate: {(total_found_and_saved/total_processed)*100}% | {total_found_and_saved}/{total_processed}")
    
    return 0


main(mode=2, music_dir=MUSIC_DIRECTORY, out_dir=OUTPUT_DIRECTORY)

