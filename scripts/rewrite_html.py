# -*- coding: utf-8 -*-
"""把 index.html 中已失效的豆包临时 CDN 链接改写为站内 assets/ 相对路径。幂等。"""
import io, os, re

MAP = {
 "qTu0VStiMH": "hero-stage.webp",
 "Do1H2t8ygG": "hero-hands.webp",
 "7IcQc50zmM": "hero-fig-linchuan.webp",
 "URHrO3BCuT": "hero-fig-xiaoman.webp",
 "tL2ijzun9k": "hero-fig-xuanchen.webp",
 "dFqsl5JtIr": "hero-fig-boss.webp",
 "CuU4jgpdrG": "hero-fig-alan.webp",
 "9h1ZEUyVY1": "drama-daoshi-cover.webp",
 "eqYjFWGAgM": "drama-zero-ep1.webp",
 "Boh0omxhVw": "drama-zero-ep2.webp",
 "eTZiK3oHUH": "drama-zero-song.webp",
 "lTz3fQ8jag": "tvc-pet-cover.jpg",
 "HwzV5SV8D0": "tvc-sofa-cover.jpg",
 "mRoyrvg6Tp": "tvc-viewarm-cover.jpg",
 "XtDh6kUylv": "tvc-qingyou-cover.webp",
 "R5LIxAD5gm": "tvc-pet.mp4",
 "lNZCi7c0sH": "tvc-sofa.mp4",
 "ng0aZuKUig": "tvc-viewarm.mp4",
 "knTRkeyFVm": "tvc-qingyou.mp4",
 "wn3onHdnaV": "splash-car-1.webp",
 "2ER42VEWBA": "splash-car-2.webp",
 "NQKBQ9kD4g": "splash-car-3.webp",
 "0TZJ66hJvj": "splash-live-1.webp",
 "dPILxZjbg1": "splash-live-2.webp",
 "0v73BUifte": "splash-live-3.webp",
 "jPVVhhKrbU": "splash-date-1.webp",
 "pQRkT83E8p": "splash-date-2.webp",
 "K9PPaoAnpZ": "splash-date-3.webp",
 "63fUiCJHpo": "ecom-pour-over-main.webp",
 "ulLVUKsgK7": "ecom-pour-over-banner.webp",
 "ZYyIAmGmvd": "ecom-qianshi-main.webp",
 "91UXl7HVV2": "ecom-qianshi-banner.webp",
 "b8PxEk662i": "ecom-lamp-main.webp",
 "L9ApPDZoXY": "ecom-lamp-banner.webp",
 "T2HsRgoU6e": "detail-cat-main.webp",
 "UHQfB8ADBr": "detail-cat-long.jpg",
 "e33AntvqdK": "detail-sun-main.webp",
 "B1laMdJhPU": "detail-sun-long.jpg",
 "Uay58NeRQS": "detail-tea-1.webp",
 "Fet9Zu6HWd": "detail-tea-2.webp",
 "EXqucjN7kV": "detail-tea-3.webp",
 "XqRNOxCLey": "detail-tea-4.webp",
 "9pjwutzZw1": "detail-tea-5.webp",
 "aZCVuTWKEs": "detail-tea-6.webp",
 "N4Aeh1q3mc": "detail-tea-7.webp",
 "8Vf2FdnVTE": "detail-tea-8.webp",
 "c5MtqRJeVb": "detail-tea-long.jpg",
 "7esVBU2pxk": "flash-1.webp",
 "1i8cANoL49": "flash-2.webp",
 "ArnV6KW87R": "flash-3.webp",
}

HTML = "index.html"
probe = os.path.join("assets", "_probe.png")
if os.path.isfile(probe):
    os.remove(probe)
    print("removed junk assets/_probe.png")

html = io.open(HTML, encoding="utf-8").read()
used, unknown = set(), set()


def repl(m):
    code = m.group(1)
    if code in MAP:
        used.add(code)
        return "assets/" + MAP[code]
    unknown.add(code)
    return m.group(0)


out = re.sub(r"https://aka\.doubaocdn\.com/s/([A-Za-z0-9]+)", repl, html)

if out != html:
    io.open(HTML, "w", encoding="utf-8").write(out)
    print("html rewritten, %d unique codes mapped" % len(used))
else:
    print("html unchanged")

missing = sorted(set(MAP) - used)
if unknown:
    print("UNMAPPED codes:", sorted(unknown))
if missing:
    print("codes in map but absent from html:", missing)
print("remaining aka refs:", len(re.findall(r"aka\.doubaocdn\.com", out)))
