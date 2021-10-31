from urllib.parse import urlsplit, unquote
from os.path import split, splitext
from datetime import datetime
from dotenv import load_dotenv

import requests
import os
import telegram


def download_image(url, filename):
    file_path = "./images/"
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    response = requests.get(url)
    response.raise_for_status()

    with open(directory + "/" + filename, "wb") as file:
        file.write(response.content)


def get_extension(url: str):
    spl = urlsplit(unquote(url))
    return splitext(split(spl.path)[1])[1]


def fetch_spacex_last_launch(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.ok:
            return response.json()
        else:
            return None
    except requests.exceptions.HTTPError:
        print("Проверьте вводимый адрес")
    except requests.exceptions.ConnectionError:
        print("Нет соединения")


if __name__ == "__main__":
    load_dotenv()
    token = os.environ["NASA_TOKEN"]

    url = "https://api.spacexdata.com/v3/launches?flight_number=94"
    responsespacex = None
    responsespacex = fetch_spacex_last_launch(url)
    if not responsespacex is None:
        images = responsespacex[0]["links"]["flickr_images"]
        for image_number, image_url in enumerate(images):
            extension = get_extension(image_url)
            filename = f"spacex{image_number + 1}{extension}"
            download_image(image_url, filename)

    url = f"https://api.nasa.gov/planetary/apod?api_key={token}&count=30"
    data_spacenasa = None
    data_spacenasa = fetch_spacex_last_launch(url)
    if not data_spacenasa is None:
        for image_number, image_url in enumerate(data_spacenasa):
            extension = get_extension(image_url["url"])
            filename = f"spacenasa{image_number + 1}{extension}"
            download_image(image_url["url"], filename)

    today = "2021-10-21"
    url = f"https://api.nasa.gov/EPIC/api/natural/date/{today}?api_key={token}"
    data_space_epic = None
    data_space_epic = fetch_spacex_last_launch(url)
    if not data_space_epic is None:
        for image_number, image_url in enumerate(data_space_epic):
            image_date = datetime.fromisoformat(image_url["date"]).strftime(
                "%Y/%m/%d")
            image = image_url["image"]
            url = f"https://api.nasa.gov/EPIC/archive/natural/{image_date}/png" \
                  f"/{image}.png?api_key={token}"
            filename = f"space_epic{image_number + 1}.png"
            download_image(url, filename)

    token = os.environ["TGM_TOKEN"]
    bot = telegram.Bot(token=token)
    updates = bot.get_updates()
    if len(updates) > 0:
        chat_id = updates[-1].effective_chat.id
        bot.send_message(chat_id=chat_id, text="First message")
