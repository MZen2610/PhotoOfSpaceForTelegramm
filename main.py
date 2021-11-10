from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import listdir
from os.path import isfile, splitext
from os.path import join as joinpath
from urllib.parse import urlsplit, unquote

import os
import requests
import telegram
import time


def save_folder(download_folder):
    directory = os.path.dirname(download_folder)
    os.makedirs(directory, exist_ok=True)
    return directory


def download_images(url, filename, directory, params={}):
    response = requests.get(url, params)
    response.raise_for_status()

    with open(f"{directory}/{filename}", "wb") as file:
        file.write(response.content)


def get_extension(url: str):
    spl = urlsplit(unquote(url))
    return splitext(spl.path)[1]


def execute_request(url: str, payload=dict()):
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.json()


def get_spacex_photos():
    url = "https://api.spacexdata.com/v3/launches/past"
    data_json = execute_request(url)
    step = 1
    images = data_json[-step]["links"]["flickr_images"]
    while len(images) == 0:
        step += 1
        images = data_json[-step]["links"]["flickr_images"]

    for image_number, image_url in enumerate(images, start=1):
        extension = get_extension(image_url)
        filename = f"spacex{image_number}{extension}"
        download_images(image_url, filename,
                        directory=save_folder("./images/"))


def get_space_nasa_photos(token):
    url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": token, "count": 30}
    data_json = execute_request(url, params)
    for image_number, image_url in enumerate(data_json, start=1):
        extension = get_extension(image_url["url"])
        filename = f"spacenasa{image_number}{extension}"
        download_images(image_url["url"], filename,
                        directory=save_folder("./images/"))


def get_space_epic_photos(token):
    today = datetime.date(datetime.today())
    url = f"https://api.nasa.gov/EPIC/api/natural/date/{today}"
    params = {"api_key": token}
    data_json = execute_request(url, params)
    step = 1
    while len(data_json) == 0:
        result_date = today - timedelta(days=step)
        url = f"https://api.nasa.gov/EPIC/api/natural/date/{result_date}"
        params = {"api_key": token}
        data_json = execute_request(url, params)
        step += 1

    for image_number, image_url in enumerate(data_json, start=1):
        image_date = datetime.fromisoformat(image_url["date"]).strftime(
            "%Y/%m/%d")
        image = image_url["image"]
        url = f"https://api.nasa.gov/EPIC/archive/natural/{image_date}/png" \
              f"/{image}.png"
        params = {"api_key": token}
        filename = f"space_epic{image_number}.png"
        download_images(url, filename, directory=save_folder("./images/"),
                        params=params)


def add_telegramm_photos(token, my_path):
    bot = telegram.Bot(token=token)
    updates = bot.get_updates()
    if len(updates) > 0:
        chat_id = updates[-1].effective_chat.id
        for path_to_file in listdir(my_path):
            if isfile(joinpath(my_path, path_to_file)):
                with open(f"{my_path}/{path_to_file}", 'rb') as file:
                    bot.send_document(chat_id=chat_id, document=file.read())
                    time.sleep(86400)

def main():
    load_dotenv()
    NASA_TOKEN = os.environ["NASA_TOKEN"]
    TGM_TOKEN = os.environ["TGM_TOKEN"]

    while True:
        try:
            get_spacex_photos()
            get_space_nasa_photos(NASA_TOKEN)
            get_space_epic_photos(NASA_TOKEN)
            add_telegramm_photos(TGM_TOKEN, "images")
        except requests.exceptions.HTTPError:
            print("Проверьте вводимый адрес")
        except requests.exceptions.ConnectionError:
            print("Нет соединения")


if __name__ == "__main__":
    main()
