from utils.insta_utils import get_client

cl = get_client()

threads = cl.direct_threads(amount=5)

for idx, thread in enumerate(threads, start=1):
    usernames = [user.username for user in thread.users]
    full_names = [user.full_name for user in thread.users]

    title = (
        thread.thread_title
        if thread.thread_title
        else ", ".join(usernames)
    )

    print(f"--- Thread #{idx} ---")
    print(f"Thread ID  : {thread.id}")
    print(f"Title      : {title}")
    print(f"Is Group   : {thread.is_group}")
    print()