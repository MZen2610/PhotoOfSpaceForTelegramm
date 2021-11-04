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


def download_image(url, filename, ifmain="./images/"):
    directory = os.path.dirname(ifmain)
    if not os.path.exists(directory):
        os.makedirs(directory)
    response = requests.get(url)
    response.raise_for_status()

    with open(f"{directory}/{filename}", "wb") as file:
        file.write(response.content)


def get_extension(url: str):
    spl = urlsplit(unquote(url))
    return splitext(spl.path)[1]


def execute_request(url: str):
    response = requests.get(url)
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

    for image_number, image_url in enumerate(images):
        extension = get_extension(image_url)
        filename = f"spacex{image_number + 1}{extension}"
        download_image(image_url, filename)


def get_photo_spacenasa():
    url = f"https://api.nasa.gov/planetary/apod?api_key={nasa_token}&count=30"
    data_spacenasa = execute_request(url)
    for image_number, image_url in enumerate(data_spacenasa):
        extension = get_extension(image_url["url"])
        filename = f"spacenasa{image_number + 1}{extension}"
        download_image(image_url["url"], filename)


def get_photo_space_epic():
    today = datetime.date(datetime.today())
    url = f"https://api.nasa.gov/EPIC/api/natural/date/{today} ?api_key" \
          f"={nasa_token}"
    data_space_epic = execute_request(url)
    step = 1
    while len(data_space_epic) == 0:
        result_date = today - timedelta(days=step)
        url = f"https://api.nasa.gov/EPIC/api/natural/date/{result_date} " \
              f"?api_key={nasa_token}"
        data_space_epic = execute_request(url)
        step += 1

    for image_number, image_url in enumerate(data_space_epic):
        image_date = datetime.fromisoformat(image_url["date"]).strftime(
            "%Y/%m/%d")
        image = image_url["image"]
        url = f"https://api.nasa.gov/EPIC/archive/natural/{image_date}/png" \
              f"/{image}.png?api_key={nasa_token}"
        filename = f"space_epic{image_number + 1}.png"
        download_image(url, filename)


def add_photo_telegramm():
    bot = telegram.Bot(token=tgm_token)
    updates = bot.get_updates()
    if len(updates) > 0:
        chat_id = updates[-1].effective_chat.id
        mypath = "images"
        for path_to_file in listdir(mypath):
            if isfile(joinpath(mypath, path_to_file)):
                bot.send_document(chat_id=chat_id, document=open(
                    f"{mypath}/{path_to_file}", 'rb'))


def main():
    try:
        get_photo_spacex()
        get_photo_spacenasa()
        get_photo_space_epic()
        add_photo_telegramm()
    except requests.exceptions.HTTPError:
        print("Проверьте вводимый адрес")
    except requests.exceptions.ConnectionError:
        print("Нет соединения")


if __name__ == "__main__":
    load_dotenv()
    nasa_token = os.environ["NASA_TOKEN"]
    tgm_token = os.environ["TGM_TOKEN"]

    while True:
        time.sleep(86400)
        main()
