Here is the complete **field-by-field payload mapping guide** for Instagram Direct Message media types, derived directly from your raw API payload (`json01.json`).

---

### 🗺️ Summary Overview Table

| # | User Media Description | Instagram API `item_type` | Primary JSON Location | Extracted `item_type` | Extracted `url` Contents |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Multi-Image Carousel (e.g. 5 photos)** | `generic_xma` | `raw_xma.generic_xma[]` | `"carousel"` | List of 5 full-res image URLs |
| **2** | **Shared Feed Post** | `xma_media_share` | `xma_share` / `raw_xma.xma_media_share[]` | `"post"` | `[target_url]` (No thumbnail) |
| **3** | **Shared Reel** | `xma_clip` | `xma_share` / `raw_xma.xma_clip[]` | `"reel"` | `[target_url]` (No thumbnail) |
| **4** | **Animated GIF** | `animated_media` (`is_sticker: false`) | `animated_media` | `"animated_gif"` | Official Giphy URL (`media.giphy.com`) |
| **5** | **Standalone Sticker** | `animated_media` (`is_sticker: true`) | `animated_media` | `"sticker"` | Official Giphy URL (`media.giphy.com`) |
| **6** | **Voice Message** | `voice_media` or `media` (`media_type: 11`)| `media` or `voice_media` | `"voice_message"` | `[audio_url]` (No thumbnail) |
| **7** | **Disappearing 1-View Photo/Video** | `raven_media` (`view_mode: "once"`) | `visual_media` | `"disappearing_photo"` / `video` | Candidates or `[]` if expired |
| **8** | **Disappearing 2-View Photo/Video** | `raven_media` (`view_mode: "replayable"`) | `visual_media` | `"disappearing_photo"` / `video` | Candidates or `[]` if expired |
| **9** | **Permanent Camera Photo/Video** | `raven_media` (`view_mode: "permanent"`) | `visual_media.media` | `"disappearing_photo"` / `video` | Full-res video `.mp4` or image URL |
| **10**| **Direct Camera/Gallery Photo** | `media` (`media_type: 1`) | `media` | `"photo"` | Full-res image candidate URL |
| **11**| **Direct Camera/Gallery Video** | `media` (`media_type: 2`) | `media` | `"video"` | Full-res video `.mp4` URL |

---

### 📖 Detailed Payload Breakdowns

#### 1. Multi-Image Carousel / Album Stack (5 Images)
* **Instagram `item_type`**: `"generic_xma"`
* **JSON Path**: `raw_xma.generic_xma` (List of JSON objects, e.g. 5 elements with `xma_layout_type: 9`)
* **Key Fields**:
  * Image URL: `raw_xma.generic_xma[i].image_versions2.candidates[0].url`
  * Fallback URL: `raw_xma.generic_xma[i].preview_url_info.url`
* **Output Format**:
  * `item_type`: `"carousel"`
  * `title`: `"Carousel album (5 images)"`
  * `url`: `["https://instagram.fblr1...jpg", "https://instagram.fblr2...jpg", ...]`

---

#### 2. Shared Feed Post
* **Instagram `item_type`**: `"xma_media_share"`
* **JSON Path**: `xma_share` or `raw_xma.xma_media_share[0]`
* **Key Fields**:
  * Target Link: `xma_share.video_url` or `raw_xma.xma_media_share[0].target_url` (Format: `https://www.instagram.com/p/{shortcode}/`)
  * Post Caption: `xma_share.title` or `raw_xma.xma_media_share[0].title_text`
  * Author Username: `xma_share.header_title_text`
* **Output Format**:
  * `item_type`: `"post"`
  * `title`: `"allen_artz_ The first-generation Suzuki Hayabusa..."`
  * `url`: `["https://www.instagram.com/p/Dbs3KzRgZ4e/"]`

---

#### 3. Shared Reel
* **Instagram `item_type`**: `"xma_clip"`
* **JSON Path**: `xma_share` or `raw_xma.xma_clip[0]`
* **Key Fields**:
  * Reel Link: `xma_share.video_url` or `raw_xma.xma_clip[0].target_url` (Format: `https://www.instagram.com/reel/{shortcode}/`)
  * Reel Author: `xma_share.header_title_text`
* **Output Format**:
  * `item_type`: `"reel"`
  * `title`: `"poetic_eye_1"`
  * `url`: `["https://www.instagram.com/reel/DYr2i0YzdzW/"]`

---

#### 4. GIFs & Stickers
* **Instagram `item_type`**: `"animated_media"`
* **JSON Path**: `animated_media`
* **Key Fields**:
  * Giphy ID: `animated_media.id` (e.g. `"Z21HJj2kz9uBG"`)
  * Type Flag: `animated_media.is_sticker` (`true` for stickers, `false` for GIFs)
  * Alt Description: `animated_media.alt_text`
* **Official URL Construction**: `https://media.giphy.com/media/{animated_media.id}/giphy.gif`
* **Output Format**:
  * `item_type`: `"animated_gif"` or `"sticker"`
  * `title`: `"Digital art gif. A sketched person blowing kisses..."`
  * `url`: `["https://media.giphy.com/media/Z21HJj2kz9uBG/giphy.gif"]`

---

#### 5. Voice Messages
* **Instagram `item_type`**: `"voice_media"` (or `"media"` with `media_type: 11`)
* **JSON Path**: `media`
* **Key Fields**:
  * Audio MP4 URL: `media.audio_url`
* **Output Format**:
  * `item_type`: `"voice_message"`
  * `title`: `None`
  * `url`: `["https://cdn.fbsbx.com/v/t59.3654-21/.../audioclip.mp4..."]`

---

#### 6. Disappearing Photos & Videos (1-View, 2-View, Permanent)
* **Instagram `item_type`**: `"raven_media"`
* **JSON Path**: `visual_media`
* **Key Fields**:
  * View Mode: `visual_media.view_mode` (`"once"`, `"replayable"`, or `"permanent"`)
  * Media Type: `visual_media.media.media_type` (`1` for Photo, `2` for Video)
  * Video Version URL: `visual_media.media.video_versions[0].url`
  * Photo Candidate URL: `visual_media.media.image_versions2.candidates[0].url`
* **Behavior on Expired Views**: If 1-view (`"once"`) or 2-view (`"replayable"`) was already opened, Instagram strips `image_versions2`. The item is **still registered** in the DB with `url: []` and title indicating view mode so no messages are lost.
* **Output Format**:
  * `item_type`: `"disappearing_photo"` or `"disappearing_video"`
  * `title`: `"Disappearing (once)"` / `"Disappearing (replayable)"`
  * `url`: `["https://scontent.cdninstagram.com/...mp4"]` or `[]` if expired.

---

#### 7. Direct Camera & Gallery Photos/Videos
* **Instagram `item_type`**: `"media"`
* **JSON Path**: `media`
* **Key Fields**:
  * Media Code: `media.media_type` (`1` = Photo, `2` = Video, `8` = Carousel)
  * Full Image Candidate: `media.image_versions2.candidates[0].url`
  * Full Video Version: `media.video_versions[0].url`
* **Output Format**:
  * `item_type`: `"photo"` or `"video"`
  * `title`: `None` (or `media.caption_text` if provided)
  * `url`: `["https://instagram.fblr1-4.fna.fbcdn.net/v/t1.15752-9/...jpg"]`