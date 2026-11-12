# -*- coding: utf-8 -*-
"""下载站点素材到 assets/ 目录（由 GitHub Actions 运行）。"""
import json, os, sys, time, urllib.request

ITEMS = [
    ("hero-hands.webp",        "https://aka.doubaocdn.com/s/tYuCwUIzSO"),
    ("hero-stage.webp",        "https://aka.doubaocdn.com/s/20i3ARca1Z"),
    ("hero-fig-linchuan.webp", "https://aka.doubaocdn.com/s/2eRNZ1gyf8"),
    ("hero-fig-xiaoman.webp",  "https://aka.doubaocdn.com/s/Ie4bez79RW"),
    ("hero-fig-xuanchen.webp", "https://aka.doubaocdn.com/s/Lo6RVUeLBh"),
    ("hero-fig-boss.webp",     "https://aka.doubaocdn.com/s/UUCOVsk7Lq"),
    ("hero-fig-alan.webp",     "https://aka.doubaocdn.com/s/GMK0PJSVPl"),

    ("drama-daoshi-cover.webp", "https://aka.doubaocdn.com/s/6f1GXvgn59"),
    ("drama-zero-ep1.webp",     "https://aka.doubaocdn.com/s/31W6ZIfRT6"),
    ("drama-zero-ep2.webp",     "https://aka.doubaocdn.com/s/Lk3G3zeRTg"),
    ("drama-zero-song.webp",    "https://aka.doubaocdn.com/s/5X785imObU"),

    ("tvc-pet-cover.jpg",     "https://aka.doubaocdn.com/s/23Pswsu6YY"),
    ("tvc-sofa-cover.jpg",    "https://aka.doubaocdn.com/s/wluvrQnfAp"),
    ("tvc-viewarm-cover.jpg", "https://aka.doubaocdn.com/s/CWR7OTgc2o"),
    ("tvc-qingyou-cover.webp","https://aka.doubaocdn.com/s/evv18FQV10"),

    ("tvc-pet.mp4",     "https://aka.doubaocdn.com/s/aDEEwZaBag"),
    ("tvc-sofa.mp4",    "https://aka.doubaocdn.com/s/gyH0V3j566"),
    ("tvc-viewarm.mp4", "https://aka.doubaocdn.com/s/ixENy4AyOz"),
    ("tvc-qingyou.mp4", "https://aka.doubaocdn.com/s/5Il5ezJe9c"),

    ("splash-car-1.webp",  "https://aka.doubaocdn.com/s/lVetGuHMD7"),
    ("splash-car-2.webp",  "https://aka.doubaocdn.com/s/UKp6lUQLVG"),
    ("splash-car-3.webp",  "https://aka.doubaocdn.com/s/hg0EjZyquC"),
    ("splash-live-1.webp", "https://aka.doubaocdn.com/s/oPN1mf6Ftw"),
    ("splash-live-2.webp", "https://aka.doubaocdn.com/s/G7QzkrqLXy"),
    ("splash-live-3.webp", "https://aka.doubaocdn.com/s/bURUMyi1Jq"),
    ("splash-date-1.webp", "https://aka.doubaocdn.com/s/JPi3fV81o9"),
    ("splash-date-2.webp", "https://aka.doubaocdn.com/s/66LECUlOSj"),
    ("splash-date-3.webp", "https://aka.doubaocdn.com/s/bTgH2hYzgd"),

    ("ecom-pour-over-main.webp",   "https://aka.doubaocdn.com/s/XlC1qszWEG"),
    ("ecom-pour-over-banner.webp", "https://aka.doubaocdn.com/s/RtZ5DqsdpS"),
    ("ecom-qianshi-main.webp",     "https://aka.doubaocdn.com/s/olqH7nEqVl"),
    ("ecom-qianshi-banner.webp",   "https://aka.doubaocdn.com/s/yZyrOYq3d5"),
    ("ecom-lamp-main.webp",        "https://aka.doubaocdn.com/s/zyojZaGg6r"),
    ("ecom-lamp-banner.webp",      "https://aka.doubaocdn.com/s/LcHcfrYHJY"),

    ("detail-cat-main.webp", "https://aka.doubaocdn.com/s/q32D9e4TgG"),
    ("detail-cat-long.jpg",  "https://aka.doubaocdn.com/s/eFCsR3Op5g"),
    ("detail-tea-1.webp",    "https://aka.doubaocdn.com/s/s9QGiObmnV"),
    ("detail-tea-2.webp",    "https://aka.doubaocdn.com/s/pnhID9XMnH"),
    ("detail-tea-3.webp",    "https://aka.doubaocdn.com/s/oCdkI8ydkh"),
    ("detail-tea-4.webp",    "https://aka.doubaocdn.com/s/zKgU2U97GR"),
    ("detail-tea-5.webp",    "https://aka.doubaocdn.com/s/URen8UHuUy"),
    ("detail-tea-6.webp",    "https://aka.doubaocdn.com/s/NrxsfSVfSk"),
    ("detail-tea-7.webp",    "https://aka.doubaocdn.com/s/6dDa607MaY"),
    ("detail-tea-8.webp",    "https://aka.doubaocdn.com/s/5BKgadKWKo"),
    ("detail-tea-long.jpg",  "https://aka.doubaocdn.com/s/YSYcKCv5rz"),
    ("detail-sun-main.webp", "https://aka.doubaocdn.com/s/KODJ7Of5Cu"),
    ("detail-sun-long.jpg",  "https://aka.doubaocdn.com/s/G3GMpsKfBU"),

    ("flash-1.webp", "https://aka.doubaocdn.com/s/q9tWVbhCdm"),
    ("flash-2.webp", "https://aka.doubaocdn.com/s/IzVIKdKVrp"),
    ("flash-3.webp", "https://aka.doubaocdn.com/s/KuzK2wB2SU"),
]

OUTDIR = "assets"
os.makedirs(OUTDIR, exist_ok=True)

ok, fail = [], []
for name, url in ITEMS:
    dst = os.path.join(OUTDIR, name)
    last_err = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            if not data:
                raise ValueError("empty body")
            with open(dst, "wb") as f:
                f.write(data)
            ok.append({"file": name, "bytes": len(data)})
            last_err = None
            break
        except Exception as e:
            last_err = repr(e)[:200]
            time.sleep(2)
    if last_err is not None:
        fail.append({"file": name, "err": last_err})

with open("assets_status.json", "w", encoding="utf-8") as f:
    json.dump({"total": len(ITEMS), "ok_count": len(ok), "fail_count": len(fail),
               "ok": ok, "fail": fail}, f, ensure_ascii=False, indent=1)

print("total=%d ok=%d fail=%d" % (len(ITEMS), len(ok), len(fail)))
for f_ in fail:
    print("FAIL", f_["file"], f_["err"])

if fail:
    sys.exit(1)
