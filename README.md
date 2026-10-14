# No Hidden Steps: video website

A small static site. Every technique video gets a permanent page at `/<slug>/`, which is what the QR codes in the book point to. Only `videos.json` knows the YouTube IDs, so a broken or re-shot video is a one-line fix and the printed QR codes never change.

## What's here

| File | What it does |
| --- | --- |
| `videos.json` | The one file you edit: every video's slug, title, YouTube ID and quick recap |
| `build.py` | Turns `videos.json` into the website (`_site/`) |
| `static/style.css` | The look (same colors and fonts as the book) |
| `check_videos.py` | Checks every YouTube ID still plays and can be embedded |
| `make_qr.py` | Makes a QR code SVG for every page, for the book layout |
| `.github/workflows/deploy.yml` | Rebuilds and publishes the site every time you commit |
| `.github/workflows/check-videos.yml` | Runs the video check every Monday and alerts you if one breaks |

## One-time setup (about 20 minutes)

1. Make a free GitHub account and a new repository, e.g. `nohiddensteps-site`.
2. Upload everything in this folder (including the hidden `.github` folder) to the repository.
3. In the repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. The site is live at `https://<your-username>.github.io/nohiddensteps-site/` within a couple of minutes.
5. **Later, once you register the domain:** in `videos.json` set `"domain_live": true` inside `"site"`, then in **Settings → Pages → Custom domain** enter `nohiddensteps.com` and follow GitHub's DNS instructions. Turn on **Enforce HTTPS**.
6. Make sure GitHub can email you: **Settings (your profile) → Notifications → Actions → "Notify me only for failed workflows"** and keep **Watching** the repository.

## Adding a video (every time you film one)

1. Upload to YouTube as **Unlisted** and make sure **Allow embedding** is on.
2. Copy the ID from the link: in `https://youtu.be/AbC123xyz`, the ID is `AbC123xyz`.
3. In `videos.json`, find the slug (e.g. `roux-stages`) and paste the ID into `"youtube_id"`. Optionally add a few `"recap"` lines.
4. Commit. The site rebuilds itself; the "Coming soon" box turns into the video.
5. Keep the original video file backed up somewhere other than YouTube.

## The weekly check (hands-off)

Every Monday GitHub asks YouTube whether each video still exists and can still be embedded. If everything is fine, nothing happens. If one has been deleted, made private, or had embedding turned off:

- the check fails and GitHub **emails you**, and
- it opens an **issue** listing exactly which page is broken and how to fix it.

You can also run it any time from the **Actions** tab → *Weekly video check* → **Run workflow**.

While a video is broken, readers still land on the right page, still see the quick recap, and still get a "Watch on YouTube" link, so nobody hits a dead end.

The check also saves `status/last-check.json` each week. That small commit keeps GitHub from pausing the schedule on a quiet repository.

## QR codes for the book

Once the domain is registered: `pip install qrcode`, then `python make_qr.py`. SVG files land in `qr/`, one per slug, ready for the book layout.

## Selling links

When the book is for sale, paste the Lulu link into `"book_links"` → `"lulu"` in `videos.json` and commit.

- **Only a Lulu link:** every "Get the book" button on the site goes straight to Lulu.
- **Lulu and Amazon links:** the buttons go to the site's book page, which shows both editions side by side: the Kitchen Edition (coil-bound, Lulu) and the Hardcover (Amazon).
- **No links yet:** the buttons go to the book page, which says the book is in testing.
