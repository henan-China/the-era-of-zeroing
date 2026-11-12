# -*- coding: utf-8 -*-
"""index.html 资源处理：
1) 把历史上失效的豆包临时 CDN 短链改写为站内 assets/ 路径；
2) 把 assets/ 引用切换到 raw.githubusercontent CDN 绝对地址（国内下载比 Pages 快约 50 倍）；
3) 为 img / video 增加回落到 assets/ 本地路径的兜底；
4) 统一四条叙事线的 TRACK 编号。
幂等：重复运行不改变结果。
"""
import io, os, re

CDN = "https://raw.githubusercontent.com/henan-China/the-era-of-zeroing/main/assets/"

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

TRACK_BY_TITLE = {"TVC 广告": "03", "电商视觉": "04",
                  "AIGC 真人剧": "02", "AIGC 漫剧": "01"}
BLOCK_BY_NAME = {"AIGC 真人剧": "02", "AIGC 漫剧": "01"}

OLD_VIDEO_ERROR = """    video.addEventListener("error", function(){
      if(started) return;
      started = true;
      loading.classList.remove("show");
      showToast("视频加载失败，请检查网络后重试");
    });"""

NEW_VIDEO_ERROR = """    video.addEventListener("error", function(){
      if(!video.dataset.fallback && (video.currentSrc || video.src).indexOf("raw.githubusercontent.com") >= 0){
        video.dataset.fallback = "1";
        video.src = "assets/" + url.split("/").pop();
        video.load();
        return;
      }
      if(started) return;
      started = true;
      loading.classList.remove("show");
      showToast("视频加载失败，请检查网络后重试");
    });"""

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


def add_img_fallback(s):
    def one(m):
        tag = m.group(0)
        name = m.group(1)
        if "onerror" in tag:
            return tag
        return tag[:-1] + " onerror=\"this.onerror=null;this.src='assets/%s'\">" % name

    return re.sub(r'<img [^>]*src="%s([A-Za-z0-9._-]+)"[^>]*>' % re.escape(CDN), one, s)


def close_img_tags(s):
    """修复历史上因加兜底属性而丢失标签结尾 > 的 img（幂等）"""
    return re.sub(r'(onerror="this\.onerror=null;this\.src=\'[^\']*\'")(?!\s*>)', r'\1>', s)


def to_cdn(s):
    if "raw.githubusercontent.com" in s:
        return add_img_fallback(s)
    s = s.replace("assets/", CDN)
    return add_img_fallback(s)


out = close_img_tags(to_cdn(out))

if OLD_VIDEO_ERROR in out:
    out = out.replace(OLD_VIDEO_ERROR, NEW_VIDEO_ERROR)
    print("video fallback handler patched")

if 'showToast("视频加载失败' in out and "video.dataset.fallback" not in out:
    print("WARN: video error handler not patched (source text changed)")


def fix_tracks(s):
    def r1(m):
        title = m.group(2).strip()
        num = TRACK_BY_TITLE.get(title)
        if not num:
            return m.group(0)
        return '<span class="t-no">TRACK %s</span>%s<h3>%s</h3>' % (num, m.group(1), title)

    def r2(m):
        name = m.group(1).strip()
        num = BLOCK_BY_NAME.get(name)
        if not num:
            return m.group(0)
        return '<span class="d-block-no">TRACK %s · %s</span>' % (num, name)

    s = re.sub(r'<span class="t-no">TRACK \d+</span>(\s*)<h3>([^<]+)</h3>', r1, s)
    s = re.sub(r'<span class="d-block-no">TRACK \d+ · ([^<]+)</span>', r2, s)
    return s


out = fix_tracks(out)

if out != html:
    io.open(HTML, "w", encoding="utf-8").write(out)
    print("html rewritten")
else:
    print("html unchanged")

missing = sorted(set(MAP) - used)
if unknown:
    print("UNMAPPED codes:", sorted(unknown))
if missing:
    print("codes in map but absent from html:", missing)
print("local assets refs:", out.count('src="assets/') + out.count("data-video=\"assets/"))
print("cdn refs:", out.count(CDN))
print("img fallbacks:", out.count("this.onerror=null"))
print("track markers:", re.findall(r"TRACK \d+", out))
