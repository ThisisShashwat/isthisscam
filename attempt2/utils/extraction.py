import datetime
from typing import List

from utils.general_utils import get_field
from utils.media_handler import download_all_urls
from utils.media_summarise import summarise_files
from utils.models import Messages

"""

item_types:


animated_media		message.animated_media

text		message.text
media		message.media
raven_media		message.visual_media
voice_media		message.media
link		message.link
like	
media_share		message.media_share
reel_share		message.reel_share
clip		message.clip
xma_share / xma_clip		message.xma_share or message.raw_xma
action_log	


"""


def extract_media(msg):

    item_type = get_field(msg, "item_type")
    media_type = None
    media_urls = None

    # 1. CAROUSEL / CUTOUT

    if item_type == "generic_xma":
        raw_xma_items = get_field(msg, "raw_xma", "generic_xma") or []
        first_item = raw_xma_items[0] if raw_xma_items else {}
        sticker_type = get_field(first_item, "sticker_type")
        attachment_id = str(get_field(first_item, "attachment_id") or "")

        # cutout
        if sticker_type or attachment_id.startswith("cutout_"):
            sticker_url = get_field(first_item, "preview_url_info", "url") or get_field(first_item, "preview_url")
            if sticker_url:
                media_type="sticker"
                media_urls=[str(sticker_url)]

        # carousel
        urls = []
        for x_item in raw_xma_items:
            candidates = get_field(x_item, "image_versions2", "candidates") or []
            if candidates:
                urls.append(get_field(candidates, 0, "url"))
            else:
                p_url = get_field(x_item, "preview_url_info", "url") or get_field(x_item, "preview_url")
                if p_url:
                    urls.append(p_url)
        if urls:
            kind = "carousel" if len(urls) > 1 else "photo"
            media_type=kind
            media_urls=[str(u) for u in urls if u]

    # 2. reel & post

    if item_type in ("xma_media_share", "xma_clip", "xma_share"):
        xma_share = get_field(msg, "xma_share") or {}
        raw_xma_list = (
            get_field(msg, "raw_xma", "xma_media_share")
            or get_field(msg, "raw_xma", "xma_clip")
            or []
        )
        raw_first = raw_xma_list[0] if raw_xma_list else {}
        target_url = (
            get_field(xma_share, "video_url")
            or get_field(xma_share, "target_url")
            or get_field(raw_first, "target_url")
        )
        title = (
            get_field(xma_share, "title")
            or get_field(raw_first, "title_text")
            or get_field(xma_share, "header_title_text")
            or get_field(raw_first, "header_title_text")
        )

        media_kind = "post"
        if item_type == "xma_clip" or (target_url and "/reel/" in str(target_url)):
            media_kind = "reel"
        if target_url:
            media_type=media_kind
            media_urls=[str(target_url)]

    # 3. gif and stickers

    if item_type == "animated_media" or get_field(msg, "animated_media"):
        anim = get_field(msg, "animated_media") or {}
        giphy_id = get_field(anim, "id")
        is_sticker = get_field(anim, "is_sticker", default=False)
        alt_text = get_field(anim, "alt_text")
        urls = []
        if giphy_id:

            urls.append(f"https://media.giphy.com/media/{giphy_id}/giphy.gif")
        else:
            fb_url = get_field(anim, "images", "fixed_height", "url") or get_field(anim, "images", "fixed_height", "mp4")
            if fb_url:
                urls.append(str(fb_url))
        kind = "sticker" if is_sticker else "animated_gif"
        if urls:
            media_type=kind
            media_urls = urls

    # 4. vms

    if item_type == "voice_media" or (get_field(msg, "media", "media_type") == 11):
        audio_url = (
            get_field(msg, "media", "audio_url")
            or get_field(msg, "voice_media", "media", "audio", "audio_src")
        )
        if audio_url:
            media_type="voice_message"
            media_urls=[str(audio_url)]

    # 5. raven

    if item_type == "raven_media" or get_field(msg, "visual_media"):
        visual = get_field(msg, "visual_media") or {}
        view_mode = get_field(visual, "view_mode", default="permanent")
        media_obj = get_field(visual, "media") or {}
        m_type = get_field(media_obj, "media_type")
        urls = []

        video_versions = get_field(media_obj, "video_versions") or []
        for vv in video_versions:
            u = get_field(vv, "url")
            if u:
                urls.append(str(u))
                break

        if not urls:
            candidates = get_field(media_obj, "image_versions2", "candidates") or []
            if candidates:
                urls.append(str(get_field(candidates, 0, "url")))
        kind = "video" if m_type == 2 else "photo"
        title_info = f"Disappearing ({view_mode})" if view_mode != "permanent" else None

        media_type=kind
        media_urls=urls

    # 6. pics & vids

    if item_type == "media" or get_field(msg, "media"):
        media_obj = get_field(msg, "media") or {}
        m_type = get_field(media_obj, "media_type")
        urls = []
        resources = get_field(media_obj, "resources") or []
        if resources:
            for res in resources:
                v_url = get_field(res, "video_versions", 0, "url") or get_field(res, "video_url")
                i_url = get_field(res, "image_versions2", "candidates", 0, "url") or get_field(res, "thumbnail_url")
                if v_url:
                    urls.append(str(v_url))
                elif i_url:
                    urls.append(str(i_url))
        else:
            v_url = get_field(media_obj, "video_versions", 0, "url") or get_field(media_obj, "video_url")
            i_url = get_field(media_obj, "image_versions2", "candidates", 0, "url") or get_field(media_obj, "thumbnail_url")
            if v_url:
                urls.append(str(v_url))
            elif i_url:
                urls.append(str(i_url))
        caption = get_field(media_obj, "caption_text") or get_field(media_obj, "title")
        kind = "video" if m_type == 2 else ("carousel" if m_type == 8 else "photo")
        if urls:
            media_type=kind
            media_urls=urls

    return {
        "media_type": media_type,
        "media_urls": media_urls,
    }


#
# def extract_reactions(msg, viewer_id: str) -> List[Reactions]:
#     reactions_list: List[Reactions] = []
#     message_id = get_field(msg, "id")
#     emoji_entries = get_field(msg, "reactions","emojis") or []
#
#     for entry in emoji_entries:
#         emoji = get_field(entry, "emoji")
#         sender_id = get_field(entry, "sender_id")
#         timestamp = get_field(entry, "timestamp")
#
#         if not emoji or sender_id is None or timestamp is None:
#             continue
#
#         sender_id = str(sender_id)
#
#         reactions_list.append(
#             Reactions(
#                 message_id=message_id,
#                 sender_id=sender_id,
#                 is_sent_by_viewer=(sender_id == str(viewer_id)),
#                 emoji=emoji,
#                 timestamp=timestamp,
#             )
#         )
#
#     return reactions_list


def extract_message(msg, cl, media_download=False, media_summary=False) -> Messages:
    message_id = get_field(msg, "id")
    if not message_id:
        if "mid.$" in get_field(msg, "message_id"):
            message_id = get_field(msg, "item_id")
    user_id = get_field(msg, "user_id")
    thread_id = get_field(msg, "thread_id")

    timestamp = get_field(msg, "timestamp")

    if not isinstance(timestamp, datetime.datetime):
        timestamp = datetime.datetime(2026, 8, 10, 5, 12, 12, 677000,
                  tzinfo=datetime.timezone(datetime.timedelta(hours=5, minutes=30)))

    is_sent_by_viewer = get_field(msg, "is_sent_by_viewer")

    item_type = get_field(msg, "item_type")

    text = get_field(msg, "text")
    reply_id = get_field(msg, "reply", "id")

    extracted_media = extract_media(msg)

    media_type = extracted_media["media_type"]
    media_urls = extracted_media["media_urls"]

    # MEDIA_TYPES = [
    #     "photo",
    #     "carousel",
    #     "sticker",
    #     "post",
    #     "reel",
    #     "animated_gif",
    #     "voice_message",
    #     "video",
    # ]

    if (media_download or media_summary) and media_urls and media_type:
        media_local_file_paths = download_all_urls(media_urls, media_type, cl, message_id)
    else:
        media_local_file_paths = None

    if media_summary and media_local_file_paths:
        media_ai_summary = summarise_files(media_local_file_paths)
    else:
        media_ai_summary = None


    return Messages(
        id=str(message_id),
        thread_id=str(thread_id),
        user_id=str(user_id),

        timestamp=timestamp,
        is_sent_by_viewer=is_sent_by_viewer,
        item_type=item_type,

        text=text,
        reply_id=str(reply_id),

        media_type=media_type,
        media_urls=media_urls,
        media_local_file_paths=media_local_file_paths,
        media_ai_summary=media_ai_summary
    )

