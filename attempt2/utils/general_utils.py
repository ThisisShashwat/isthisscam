import datetime


def get_field(obj, *keys, default = None):
    curr = obj
    for key in keys:
        if curr is None:
            return default
        if isinstance(key, int):
            if isinstance(curr, (list, tuple)) and 0 <= key < len(curr):
                curr = curr[key]
            else:
                return default
        elif isinstance(curr, dict):
            curr = curr.get(key)
        else:
            curr = getattr(curr, str(key), None)
    return curr if curr is not None else default


def parse_datetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")