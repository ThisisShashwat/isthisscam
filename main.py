import os
from pathlib import Path
from instagrapi import Client
from dotenv import load_dotenv
load_dotenv()

SESSION_FILE = "ig_session.json"
cl = Client()

if Path(SESSION_FILE).exists():
    cl.load_settings(SESSION_FILE)
else:
    cl.login_by_sessionid(os.environ["IG_SESSIONID"])
    cl.dump_settings(SESSION_FILE)

user_id = cl.user_id_from_username("iamshashhh")
medias = cl.user_medias(user_id, 20)
print(medias)