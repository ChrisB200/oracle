import json
import logging

from flask import Blueprint, jsonify, request

from bot.client import client, send_dm, send_plex_embed
from services.redis import redis
from services.torrent import get_torrent_by_hash

routes = Blueprint("routes", __name__)

logger = logging.getLogger(__name__)


@routes.post("/torrent/completed")
def completed_torrent():
    hash = request.json.get("hash")

    if not request.json:
        return jsonify("Missing json"), 400

    if not hash:
        return jsonify("Missing hash"), 400

    user_id = redis.get(hash)

    if not user_id:
        return jsonify("Could not get user id from hash"), 400

    user_id = int(user_id)

    torrent = get_torrent_by_hash(hash)

    if not torrent:
        redis.delete(hash)
        return jsonify("could not get torrent from hash"), 400

    redis.delete(hash)

    message = f"{torrent.name} has completed downloading"

    client.loop.create_task(send_dm(user_id, message))
    return jsonify("success"), 200


@routes.post("/plex/webhooks")
def plex_webhooks():
    body = request.form
    if "payload" not in body:
        logger.error("No payload field found!")
        return jsonify({"error": "no payload"}), 400

    # Parse the JSON hidden inside the form
    payload = json.loads(body["payload"])

    event = payload.get("event")
    account = payload.get("Account")
    server = payload.get("Server")
    metadata = payload.get("Metadata")

    # Debug
    print("Plex payload parsed:", payload)

    # Now schedule the embed task
    client.loop.create_task(send_plex_embed(event, account, server, metadata))
    return jsonify({"status": "ok"}), 200
