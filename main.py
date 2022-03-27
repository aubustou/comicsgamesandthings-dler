import asyncio
from pathlib import Path
import requests
from bs4 import BeautifulSoup

from http.cookiejar import MozillaCookieJar
import aiohttp

END_PAGE = 21
URL = "https://comicsgamesandthings.com/accounts/profile/downloads/?page_number={}&search=&order_by=-date_files_last_updated&page_size=10&partner="
COOKIES_FILE_PATH = Path("cookies.txt")
DOWNLOAD_FILE = Path("downloads.txt")

cookie_jar = MozillaCookieJar("toto_cookies.txt")
# async_cookie_jar = aiohttp.CookieJar()
async_cookie_jar = {
    "csrftoken": "gmc1Jg0U68gE9f25uLs1slHQksEWu0dBc85Zul4kMvLy6gGPZppiaH8dzx8Rn9Of",
    "messages": ".eJyLjlaKj88qzs-Lz00tLk5MT1XSMdAxMtVRCi5NTgaKpJXm5FQqFGem56WmKGTmKSQWK5Tkl-TrKcXqkK0zFgBOsChP:1nY8Lg:p6AP00FDar_SMKcsACtXT_t1C_4NVHZI1ykVbOX9kN0",
    "sessionid": "46bjhzlt68fi8rcf1tfyc4um0l1fgdkr"
}

cookie_jar.load(str(COOKIES_FILE_PATH))
# async_cookie_jar.load(str(COOKIES_FILE_PATH))

print(cookie_jar)

async def main():
    download_urls = {}
    async with aiohttp.ClientSession(cookies=async_cookie_jar) as session:
        for page_number in range(1, END_PAGE + 1):
            async with session.get(URL.format(str(page_number))) as response:
                content = await response.text()

            soup = BeautifulSoup(content)
            objects = list(soup.find_all("div", class_="row no-gutters"))

            for obj in objects:
                name = obj.find_next("h2").text
                print(name)

                button = obj.find_next("button")
                di_id = button.attrs.get("di_id")
                downloadable_id = button.attrs.get("downloadable_id")

                dl_url = f"https://comicsgamesandthings.com/download/multi/{di_id}/{downloadable_id}/"
                async with session.get(dl_url) as response:
                    json_ = await response.json()
                    dl_files = json_["files_to_download"]

                for file_ in dl_files:
                    dl_file_url = f'https://comicsgamesandthings.com/download/{di_id}/{file_["id"]}/'
                    async with session.get(dl_file_url) as response:
                        dl_file_content = await response.json()

                    seed = dl_file_content["seed1"]
                    file_name = dl_file_content["clean_name"]
                    download_urls.setdefault(name, {})[file_name] = seed

                    print(f"Download {file_name}")

                    # path = Path(f"{name}/{file_name}")
                    # if path.exists():
                    #     continue
                    # path.parent.mkdir(parents=True, exist_ok=True)

                    # content = requests.get(seed, cookies=cookie_jar).content
                    # if path.suffix == ".obj":
                    #     content = content.replace(b"//", b"")
                    # path.write_bytes(content)

                import json
                json.dump(download_urls, DOWNLOAD_FILE.open("w"), indent=4)

asyncio.run(main())
