import time
from attempt2.utils.insta_utils import get_client
cl = get_client()
#
# threads = cl.direct_threads(amount=5)
#
# for t in threads:
#     print("=" * 50)
#     print("Thread ID:", t.id)
#     print("Users:", [u.username for u in t.users])
#     print("Title:", t.thread_title)


META_AI_THREADID_RHEA = 340282366841710301244259187832731991026
META_AI_THREADID_MAIN = 340282366841710301244259379693981671242

current_threadid = META_AI_THREADID_MAIN
#
REEL_URL = "https://www.instagram.com/reel/DY3IoMYqIcq/"

media_pk = cl.media_pk_from_url(REEL_URL)



cl.direct_media_share(
    media_id=media_pk,
    thread_ids=[current_threadid]
)

time.sleep(10)

messages = cl.direct_messages(current_threadid, amount=1)
if messages:
    msg = messages[0]

    if msg.raw_xma and "generic_xma" in msg.raw_xma:
        generic_xma_list = msg.raw_xma["generic_xma"]
        if generic_xma_list:
            unified = generic_xma_list[0].get("unified_response", {})
            sections = unified.get("sections", [])

            if sections:
                meta_text = sections[0]["view_model"]["primitive"]["text"]
                print(meta_text)



#
# cl.direct_answer(
#     current_threadid,
#     "can u explain this reel further in atmost detail possible? please dont use markdown or any formatting, reply in plain text."
# )
#
# time.sleep(15)
#
# messages = cl.direct_messages(current_threadid, amount=1)
# if messages:
#     msg = messages[0]
#
#     if msg.raw_xma and "generic_xma" in msg.raw_xma:
#         generic_xma_list = msg.raw_xma["generic_xma"]
#         if generic_xma_list:
#             unified = generic_xma_list[0].get("unified_response", {})
#             sections = unified.get("sections", [])
#
#             if sections:
#                 meta_text = sections[0]["view_model"]["primitive"]["text"]
#                 print(meta_text)
#
#
