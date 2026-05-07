import logging

import requests

from client import client
from config.settings import ALFRED_URL
from services.messaging import send_channel, send_dm, send_download_complete

logger = logging.getLogger()


def get_magnet_hash(magnet: str):
    marker = "btih:"
    start = magnet.find(marker)
    if start == -1:
        return None
    start += len(marker)

    end = magnet.find("&", start)
    if end == -1:
        end = len(magnet)

    return magnet[start:end].lower()


def search_library(library: str, media: str):
    response = requests.post(
        f"{ALFRED_URL}/library/{library}/search",
        json={"media": media},
        timeout=15,
    )
    response.raise_for_status()
    return response.json().get("results", [])


def download_media(library: str, magnet: str, user_id: str, platform: str):
    response = requests.post(
        f"{ALFRED_URL}/library/download",
        json={
            "magnet": magnet,
            "library": library,
            "user_id": user_id,
            "platform": platform,
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json() if response.text else {"message": "Success"}


def get_progress(library: str | None = None):
    params = {"library": library} if library else None
    response = requests.get(
        f"{ALFRED_URL}/library/progress",
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def get_storage():
    response = requests.get(f"{ALFRED_URL}/library/storage", timeout=15)
    response.raise_for_status()
    return response.json()


def download_completed(data: dict):
    user_id = data.get("user_id")
    platform = data.get("platform")
    name = data.get("name")

    if not user_id or not platform or not name:
        return

    if platform == "discord":
        print("discord")
        client.loop.create_task(send_dm(user_id, f"**Completed download**\n{name}"))
        client.loop.create_task(
            send_download_complete(
                int(user_id),
                name,
            )
        )
