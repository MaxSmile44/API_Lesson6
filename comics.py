import requests
import telegram
from dotenv import load_dotenv

import os
import shutil
from pathlib import Path
from random import randint


def save_file(url, path, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(f'{path}/{filename}', 'wb') as file:
        file.write(response.content)


def get_comic(url, path):
    """Get url to comic image, number of comic and save to directory

    Args:
        url (str): url of comic image
        path (str): path of directory to save comic

    """
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()
    img = comics['img']
    num = comics['num']
    save_file(img, path, f'comic_{num}.png')


def get_last_comic_num():
    """Find out how many comics on web page"""
    return requests.get('https://xkcd.com/info.0.json').json()['num']


def get_comment(url):
    return requests.get(url).json()['alt']


def delete_comic(path):
    shutil.rmtree(path)


def send_message_tg_bot(tg_token, chat_id, path, comment):
    bot = telegram.Bot(token=tg_token)
    with open(path, "rb") as photo:
        bot.send_photo(chat_id=chat_id, photo=photo)
    bot.send_message(chat_id=chat_id, text=comment)


def main():
    try:
        load_dotenv()
        tg_token = os.environ['TG_TOKEN']
        chat_id = os.environ['TG_CHAT_ID']
    except KeyError as error:
        print(f'KeyError: {error}')
        raise SystemExit
    folder_path = Path("./images/")
    try:
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        last_comic = get_last_comic_num()
        random_comic = randint(0, last_comic)
        url = f'https://xkcd.com/{random_comic}/info.0.json'

        get_comic(url, folder_path)
        comment = get_comment(url)

        filename = os.listdir(folder_path)[0]
        tg_path = Path(f'{folder_path}/{filename}')
        send_message_tg_bot(tg_token, chat_id, tg_path, comment)
    except ValueError as error:
        print(f'ValueError: {error}')
    finally:
        delete_comic(folder_path)


if __name__ == '__main__':
    main()
