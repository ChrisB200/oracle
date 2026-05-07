import logging

from flask import Blueprint, jsonify, request

from services.alfred import download_completed
from services.messaging import send_dm

logger = logging.getLogger(__name__)
alfred = Blueprint("alfred", __name__)


@alfred.route("/webhook", methods=["POST"])
def webhook():
    webhook_type = request.json.get("type")
    if not webhook_type:
        return jsonify("No webhook type provided", 400)

    match webhook_type:
        case "DOWNLOAD_COMPLETED":
            download_completed(request.json)

    return jsonify("success"), 200
