import requests
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils.config import CHROME_BINARY, DRIVER_PATH, TRACK_CSS_SELECTOR, LYRICS_SOURCES, SPOTIFY_DC_TOKEN
from utils.helpers import human_delay, extract_spotify_lyrics
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from syrics.api import Spotify


sp = Spotify(SPOTIFY_DC_TOKEN)

# Set Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = CHROME_BINARY
# REQUIRED (new headless, not the legacy garbage)
chrome_options.add_argument("--headless=new")
# Performance
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Stability for SPAs
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-background-timer-throttling")
chrome_options.add_argument("--disable-backgrounding-occluded-windows")
chrome_options.add_argument("--disable-renderer-backgrounding")
# Anti-flake
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# Optional but recommended (Spotify sometimes behaves differently)
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


chrome_service = Service(executable_path=DRIVER_PATH)
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
print("----Chrome driver was started----")


"""
# General Variables Declaration
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]
BASE_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    # kill keep-alive to avoid poisoned TLS sockets
    "Connection": "close",
}
_retry = Retry(
    total=2,
    backoff_factor=1.5,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"],
    raise_on_status=False,
)

_adapter = HTTPAdapter(max_retries=_retry)

# Session factory
def new_session() -> requests.Session:
    s = requests.Session()
    s.mount("https://", _adapter)
    headers = BASE_HEADERS.copy()
    headers["User-Agent"] = random.choice(UA_POOL)
    s.headers.update(headers)
    return s


# Global session (rotated)
_session = new_session()
_request_count = 0
SESSION_ROTATE_EVERY = 7
"""


def lyrics_lrclib(search_query: str) -> str | bool:
    """
    Fetch lyrics json response from lrclib.

    Args:
        search_query: clean search query.

    Returns:
        JSON list if found, otherwise None.
    """
    global _session, _request_count

    # rotate session periodically
    _request_count += 1
    if _request_count % SESSION_ROTATE_EVERY == 0:
        try:
            _session.close()
        finally:
            _session = new_session()

    human_delay(mean=2.5)

    try:
        response = _session.get(
            "https://lrclib.net/api/search",
            params={
                "q": search_query,
                "limit": random.choice([10, 15, 20]),
            },
            timeout=(3, 10),
            allow_redirects=True,
        )

    except requests.exceptions.SSLError:
        # poisoned TLS session → hard reset
        try:
            _session.close()
        finally:
            _session = new_session()
        return False

    except requests.exceptions.RequestException:
        return False

    # explicit rate-limit handling
    if response.status_code == 429:
        time.sleep(random.uniform(60, 120))
        return False

    if response.status_code != 200:
        return False

    try:
        data = response.json()
    except ValueError:
        return False

    # small post-request pause
    human_delay(mean=3.0)

    return data

def lyrics_musixmatch_via_spotify(search_query: str) -> str|bool:
    """
    Fetch lyrics json response from musixmatch_via_spotify
    
    Args:
        search_query: clean search query.

    Returns:
        Lyrics(str) if found, otherwise False
    """
    url = f"https://open.spotify.com/search/{requests.utils.quote(search_query)}/tracks"
    driver.get(url)

    first_track = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, TRACK_CSS_SELECTOR)))

    old_url = driver.current_url
    first_track.click()
    WebDriverWait(driver, 30).until(lambda d: d.current_url != old_url and "/track/" in d.current_url)

    track_url = driver.current_url
    print(track_url)
    match = re.search(r"/track/([A-Za-z0-9]+)", track_url)
    track_id = match.group(1)
    # print(track_id)

    json_response = sp.get_lyrics(track_id=track_id)
    # print(json_response)
    lyrics = extract_spotify_lyrics(json_data=json_response)
    try:
        return lyrics
    except:
        return False



"""
query_list = ["Chokra Jawaan"] # ,"Bezubaan Phir Se ABCD 2","Jaane Bhi De Heyy Babyy","Ha Raham Mehfuz"
for index, query in enumerate(query_list):
    print(f"starting - {index}")
    lyrics = lyrics_musixmatch_via_spotify(search_query=query)

    if lyrics:
        with open(f"lyrics/{query}.lrc", "w", encoding="utf-8") as f:
            f.write(lyrics)
        print("SUCCESS - Lyrics found")
    else: print("FAILURE - No lyrics found")

"""