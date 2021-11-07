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


def save_folder(ifmain):
    directory = os.path.dirname(ifmain)
    os.makedirs(directory, exist_ok=True)
    return directory


def download_image(url, filename, params={}, folder_with_photo="./images/"):
    directory = save_folder(folder_with_photo)

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


def get_photo_spacex():
    url = "https://api.spacexdata.com/v3/launches/past"
    data_spacex = execute_request(url)
    step = 1
    images = data_spacex[-step]["links"]["flickr_images"]
    while len(images) == 0:
        step += 1
        images = data_spacex[-step]["links"]["flickr_images"]

    for image_number, image_url in enumerate(images, start=1):
        extension = get_extension(image_url)
        filename = f"spacex{image_number}{extension}"
        download_image(image_url, filename, folder_with_photo="./images/")


def get_photo_spacenasa(token):
    url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": token, "count": 30}
    data_spacenasa = execute_request(url, params)
    for image_number, image_url in enumerate(data_spacenasa, start=1):
        extension = get_extension(image_url["url"])
        filename = f"spacenasa{image_number}{extension}"
        download_image(image_url["url"], filename,
                       folder_with_photo="./images/")


def get_photo_space_epic(token):
    today = datetime.date(datetime.today())
    url = f"https://api.nasa.gov/EPIC/api/natural/date/{today}"
    params = {"api_key": token}
    data_space_epic = execute_request(url, params)
    step = 1
    while len(data_space_epic) == 0:
        result_date = today - timedelta(days=step)
        url = f"https://api.nasa.gov/EPIC/api/natural/date/{result_date}"
        params = {"api_key": token}
        data_space_epic = execute_request(url, params)
        step += 1

    for image_number, image_url in enumerate(data_space_epic, start=1):
        image_date = datetime.fromisoformat(image_url["date"]).strftime(
            "%Y/%m/%d")
        image = image_url["image"]
        url = f"https://api.nasa.gov/EPIC/archive/natural/{image_date}/png" \
              f"/{image}.png"
        params = {"api_key": token}
        filename = f"space_epic{image_number}.png"
        download_image(url, filename, params, folder_with_photo="./images/")


def add_photo_telegramm(token, mypath):
    bot = telegram.Bot(token=token)
    updates = bot.get_updates()
    if len(updates) > 0:
        chat_id = updates[-1].effective_chat.id
        for path_to_file in listdir(mypath):
            if isfile(joinpath(mypath, path_to_file)):
                with open(f"{mypath}/{path_to_file}", 'rb') as file:
                    bot.send_document(chat_id=chat_id, document=file.read())


def main():
    load_dotenv()
    nasa_token = os.environ["NASA_TOKEN"]
    tgm_token = os.environ["TGM_TOKEN"]

    while True:
        try:
            get_photo_spacex()
            get_photo_spacenasa(nasa_token)
            get_photo_space_epic(nasa_token)
            add_photo_telegramm(tgm_token, "images")
        except requests.exceptions.HTTPError:
            print("Проверьте вводимый адрес")
        except requests.exceptions.ConnectionError:
            print("Нет соединения")

        time.sleep(86400)


if __name__ == "__main__":
    main()
