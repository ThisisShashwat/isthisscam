import json
from utils.insta_utils import get_client, get_thread_id

cl = get_client()
THREAD_ID = get_thread_id(cl, test=True)


def handle_realtime_sub(payload):
    print("RAW149:", json.dumps(payload, default=str)[:500])

cl.realtime_on("realtime_sub", handle_realtime_sub)

rt = cl.realtime_connect()
rt.direct_subscribe()

DIRECT_TYPING_QUERY_ID = "17867973967082385"
def gql_sub(query_id: str, input_data: dict) -> str:
    return f"1/graphqlsubscriptions/{query_id}/" + json.dumps(
        {"input_data": input_data}, separators=(",", ":")
    )
rt.graph_ql_subscribe(gql_sub(DIRECT_TYPING_QUERY_ID, {"user_id": str(cl.user_id)}))

try:
    rt.ping()
    while True:
        try:
            cl.realtime_read_once()
        except TimeoutError:
            continue
except KeyboardInterrupt:
    pass
finally:
    cl.realtime_disconnect()
