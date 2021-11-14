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


def create_folder(download_folder):
    directory = os.path.dirname(download_folder)
    os.makedirs(directory, exist_ok=True)
    return directory


def download_image(url, filename, directory, params={}):
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


def download_spacex_photos():
    url = "https://api.spacexdata.com/v3/launches/past"
    query_string = execute_request(url)
    step = 1
    images = query_string[-step]["links"]["flickr_images"]
    while len(images) == 0:
        step += 1
        images = query_string[-step]["links"]["flickr_images"]

    for image_number, image_url in enumerate(images, start=1):
        extension = get_extension(image_url)
        filename = f"spacex{image_number}{extension}"
        download_image(image_url, filename, directory=create_folder(
            "./images/"))


def download_space_nasa_photos(token):
    url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": token, "count": 30}
    query_string = execute_request(url, params)
    for image_number, image_url in enumerate(query_string, start=1):
        extension = get_extension(image_url["url"])
        filename = f"spacenasa{image_number}{extension}"
        download_image(image_url["url"], filename,
                       directory=create_folder("./images/"))


def download_space_epic_photos(token):
    today = datetime.date(datetime.today())
    url = f"https://api.nasa.gov/EPIC/api/natural/date/{today}"
    params = {"api_key": token}
    query_string = execute_request(url, params)
    step = 1
    while len(query_string) == 0:
        result_date = today - timedelta(days=step)
        url = f"https://api.nasa.gov/EPIC/api/natural/date/{result_date}"
        params = {"api_key": token}
        query_string = execute_request(url, params)
        step += 1

    for image_number, image_url in enumerate(query_string, start=1):
        image_date = datetime.fromisoformat(image_url["date"]).strftime(
            "%Y/%m/%d")
        image = image_url["image"]
        url = f"https://api.nasa.gov/EPIC/archive/natural/{image_date}/png" \
              f"/{image}.png"
        params = {"api_key": token}
        filename = f"space_epic{image_number}.png"
        download_image(url, filename, directory=create_folder("./images/"),
                       params=params)


def enumeration_and_send_photo(bot, path, chat_id):
    for path_to_file in listdir(path):
        if isfile(joinpath(path, path_to_file)):
            with open(f"{path}/{path_to_file}", 'rb') as file:
                bot.send_document(chat_id=chat_id, document=file)
                time.sleep(86400)


def publish_telegramm_photos(token, chat_id, path):
    bot = telegram.Bot(token=token)
    enumeration_and_send_photo(bot, path, chat_id)


def main():
    load_dotenv()
    nasa_token = os.environ["NASA_TOKEN"]
    tgm_token = os.environ["TGM_TOKEN"]
    chat_id = os.environ["CHAT_ID"]

    while True:
        try:
            download_spacex_photos()
            download_space_nasa_photos(nasa_token)
            download_space_epic_photos(nasa_token)
            publish_telegramm_photos(tgm_token, chat_id, "images")
        except requests.exceptions.HTTPError:
            print("Проверьте вводимый адрес")
        except requests.exceptions.ConnectionError:
            print("Нет соединения")


if __name__ == "__main__":
    main()
