import os

from instagrapi import Client
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

def get_client(session_file="default"):

    if session_file == "default":
        SESSION_FILE = "../../ig_session.json"
        SESSION_ID = os.environ["IG_SESSIONID"]
    else:
        SESSION_FILE = "../../ig_session_other.json"
        SESSION_ID = os.environ["IG_SESSIONID_OTHER"]

    cl = Client()

    if Path(SESSION_FILE).exists():
        cl.load_settings(SESSION_FILE)
    else:
        cl.login_by_sessionid(SESSION_ID)
        cl.dump_settings(SESSION_FILE)

    return cl

def get_thread_id(cl):
    target_id = cl.user_id_from_username("ishaanirl.exe")
    thread = cl.direct_thread_by_participants([int(target_id)])
    return thread["thread"]["thread_id"]