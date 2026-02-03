import requests
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from syrics.api import Spotify
from config import SPOTIFY_TRACK_CSS_SELECTOR
from utils.helpers import extract_spotify_lyrics, build_search_query, match_song_metadata
from utils.selenium_startup import get_driver
from dotenv import load_dotenv
import os
import logging
from bs4 import BeautifulSoup
import json

load_dotenv()
SPOTIFY_DC_TOKEN = os.getenv("SPOTIFY_DC_TOKEN")

log = logging.getLogger(__name__)
sp = Spotify(SPOTIFY_DC_TOKEN)
driver = get_driver()


def fetch_lyrics(song_path: str) -> tuple:
    """
    Fetch lyrics from musixmatch-via-spotify
    
    :param song_path: song path
    :type song_path: str
    :return: (synced_lyrics, unsynced_lyrics) items can be str|False
    :rtype: tuple

    """
    cache = {
        "synced_lyrics":False,
        "unsynced_lyrics":False
    }


    search_query = build_search_query(song_path=song_path)
    # print(search_query)
    url = f"https://open.spotify.com/search/{requests.utils.quote(search_query)}/tracks"

    try:
        driver.get(url)
        first_track = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, SPOTIFY_TRACK_CSS_SELECTOR)))
    except: 
        log.info("Spotify: selenium (driver get) time out | check internet speed!")
        return (False, False)

    old_url = driver.current_url
    first_track.click()
    WebDriverWait(driver, 30).until(lambda d: d.current_url != old_url and "/track/" in d.current_url)

    track_url = driver.current_url
    # print(track_url)

    #/start For track comparison 
    resp = requests.get(track_url,headers={"User-Agent": "Mozilla/5.0"},timeout=10)
    if resp.status_code != 200:
        return (False, False)    # continue any way

    soup = BeautifulSoup(resp.text, "html.parser")
    def meta(prop):
        tag = soup.find("meta", property=prop)
        return tag["content"] if tag else None
    
    recieved_song_info = f'{meta("og:title")} {meta("og:description")}'
    
    flag = match_song_metadata(local_song_path=song_path, received_song_info=recieved_song_info, threshold=70)

    if flag is False: return (False, False)
    #/end For track comparison 

    match = re.search(r"/track/([A-Za-z0-9]+)", track_url)
    track_id = match.group(1)
    # print(track_id)

    json_response = sp.get_lyrics(track_id=track_id)
    # print(json_response)
    # with open(f"_lyrics/{meta("og:title")}.json", "w", encoding="utf-8") as f:
    #     json.dump(json_response, f, ensure_ascii=False, indent=2)

    lyrics = extract_spotify_lyrics(json_data=json_response)
    try: 
        cache["synced_lyrics"] = lyrics[0]
        cache["unsynced_lyrics"] = lyrics[1]
    except: pass
        

    return (cache["synced_lyrics"], cache["unsynced_lyrics"])    



if __name__ == "__main__":
    SONG_PATHS = [
        "C:\\Users\\Max\\Desktop\\music\\small\\Sunidhi Chauhan - Tanha Tere Bagair.flac", # musixmatch only
        "C:\\Users\\Max\\Desktop\\music\\small\\Shreya Ghoshal - Cry Cry.flac", # lrclib only
        "C:\\Users\\Max\\Desktop\\music\\small\\Outstation - Tum Se.flac", # both
        "C:\\Users\\Max\\Desktop\\music\\small\\Heil Hitler Kanye West.flac" # none
        ]
    for i, song in enumerate(SONG_PATHS):
        print(f"{i+1}. {song}")
        synced, unsynced =  fetch_lyrics(song_path=song)
        with open(f"_lyrics/{i+1}.lrc", "w", encoding="utf-8") as f:
            f.write(f"\n{song}\nsynced\n\n{synced}")
            f.write(f"\n{song}\nunsynced\n\n{unsynced}")


