from config import RECIPIENT_USERNAME, IG_SESSIONID, IG_SESSIONID_OTHER
from utils.db_utils import get_latest_message_id

from instagrapi import Client

from instagrapi.extractors import extract_direct_thread
from pathlib import Path


def get_client(session_file="default"):

    if session_file == "default":
        SESSION_FILE = "../../ig_session.json"
        SESSION_ID = IG_SESSIONID
    else:
        SESSION_FILE = "../../ig_session_other.json"
        SESSION_ID = IG_SESSIONID_OTHER

    cl = Client()

    if Path(SESSION_FILE).exists():
        cl.load_settings(SESSION_FILE)
    else:
        cl.login_by_sessionid(SESSION_ID)
        cl.dump_settings(SESSION_FILE)

    return cl

def get_thread_id(cl, test=False):
    if test: return str(340282366841710301281153262129164814061)
    target_id = cl.user_id_from_username(RECIPIENT_USERNAME)
    thread = cl.direct_thread_by_participants([int(target_id)])
    return str(thread["thread"]["thread_id"])


def fetch_new_messages(thread_id, cl, session, page_limit=20):
    latest_known_id = get_latest_message_id(session, thread_id)

    print(latest_known_id)
    if latest_known_id is None:
        return sorted(cl.direct_thread(thread_id, amount=0).messages, key=lambda m: m.timestamp)

    assert cl.user_id, "Login required"
    params = {
        "visual_message_return_type": "unseen",
        "direction": "older",
        "seq_id": "40065",
        "limit": str(page_limit),
    }
    cursor = None
    items = []

    while True:
        if cursor:
            params["cursor"] = cursor

        result = cl.private_request(f"direct_v2/threads/{thread_id}/", params=params)
        thread_data = result["thread"]
        stop = False
        for item in thread_data["items"]:
            print(item.get("item_id"))
            if item.get("item_id") == str(latest_known_id):
                stop = True
                break

            if item.get("item_id") not in {i.get("item_id") for i in items}:
                items.append(item)
            # items.append(item)

        if stop:
            break

        cursor = thread_data.get("oldest_cursor")
        if not cursor:
            break

    thread_data["items"] = items
    messages = extract_direct_thread(thread_data).messages
    return sorted(messages, key=lambda m: m.timestamp)
