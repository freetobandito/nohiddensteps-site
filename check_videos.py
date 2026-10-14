#!/usr/bin/env python3
"""Check that every YouTube video in videos.json still plays and can be embedded.

Uses YouTube's public oEmbed endpoint, which answers for public and unlisted videos
and refuses ones that were deleted, made private, or had embedding turned off.
Exits with code 1 (and writes broken.md) if anything is broken, so the GitHub
workflow can open an issue and email you.
"""
import json, os, sys, time, urllib.request, urllib.error, urllib.parse, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
videos = json.load(open(os.path.join(ROOT, "videos.json"), encoding="utf-8"))["videos"]

def check(video_id):
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(f"https://www.youtube.com/watch?v={video_id}")
    last = None
    for attempt in range(3):                      # retry so a one-off network hiccup isn't reported
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "nohiddensteps-link-check"}), timeout=20) as r:
                return r.status == 200, f"HTTP {r.status}"
        except urllib.error.HTTPError as e:
            reason = {401: "embedding disabled or video private", 403: "video private or blocked",
                      404: "video deleted or ID wrong", 400: "video deleted or ID wrong"}.get(e.code, "")
            return False, f"HTTP {e.code} {reason}".strip()
        except Exception as e:                    # timeouts, DNS, etc.
            last = str(e)
            time.sleep(5 * (attempt + 1))
    return None, f"could not reach YouTube ({last})"

broken, unreachable, ok, pending = [], [], 0, 0
for v in videos:
    vid = v.get("youtube_id", "").strip()
    if not vid:
        pending += 1
        continue
    good, detail = check(vid)
    if good:
        ok += 1
    elif good is None:
        unreachable.append((v, detail))
    else:
        broken.append((v, detail))

stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
print(f"{stamp}: {ok} OK, {len(broken)} broken, {len(unreachable)} unreachable, {pending} not filmed yet")
os.makedirs(os.path.join(ROOT, "status"), exist_ok=True)
json.dump({"checked": stamp, "ok": ok, "broken": [v["slug"] for v, _ in broken], "not_filmed": pending},
          open(os.path.join(ROOT, "status", "last-check.json"), "w"), indent=2)

if broken:
    lines = [f"The weekly check found {len(broken)} technique video(s) that no longer play on the site.", "",
             "| Page | Video ID | Problem |", "| --- | --- | --- |"]
    lines += [f"| /{v['slug']} | `{v['youtube_id']}` | {d} |" for v, d in broken]
    lines += ["", "**To fix:** upload the video again (from your backup), copy its new ID into `videos.json` for that slug, and commit.",
              "The site rebuilds itself and every printed QR code keeps working."]
    open(os.path.join(ROOT, "broken.md"), "w").write("\n".join(lines) + "\n")
    for v, d in broken:
        print(f"BROKEN /{v['slug']}: {d}")
    sys.exit(1)
