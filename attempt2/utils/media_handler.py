from config import MEDIA_DIR
import mimetypes
import requests
from pathlib import Path
from urllib.parse import urlparse

def download_url(url, message_id, index, media_type):
    resp = requests.get(url, stream=True, timeout=30)
    resp.raise_for_status()

    ext = mimetypes.guess_extension((resp.headers.get("Content-Type") or "").split(";")[0])
    ext = ext or Path(urlparse(url).path).suffix or ".bin"
    dest_dir = Path(MEDIA_DIR)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"{message_id}_{index}_{media_type}{ext}"

    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    return str(dest_path)


def resolve_urls(urls, media_type, cl):

    if media_type in ("post", "reel"):

        new_urls = []

        for url in urls:
            media_pk = cl.media_pk_from_url(url)
            info = cl.media_info(media_pk)

            if media_type == "reel":
                url = info.video_url
                if url: new_urls.append(url)

            elif media_type == "post":
                if info.resources:
                    for resource in info.resources:
                        media_url = resource.video_url or resource.thumbnail_url
                        if media_url: new_urls.append(media_url)

                post_url = info.video_url or info.thumbnail_url
                if post_url: new_urls.append(post_url)

        return new_urls

    else:
        return urls

def download_all_urls(urls, media_type, cl, message_id):
    file_paths = []

    new_urls = resolve_urls(urls, media_type, cl)

    for i, url in enumerate(new_urls):
        file_path = download_url(url, message_id, i, media_type)
        if file_path: file_paths.append(file_path)

    return file_paths