# -*- coding: utf-8 -*-
"""index.html 素材源与播放兜底处理。
1) 图片/视频统一切到 media.doubao.com 长期直链（国内可访问，比 GitHub Pages 快得多）；
2) 为 img、图片弹层大图、视频补 assets/ 本地回落；
3) 统一四条叙事线的 TRACK 编号。
幂等：重复运行不改变结果。
"""
import io, os, re, json

CDN = "https://raw.githubusercontent.com/henan-China/the-era-of-zeroing/main/assets/"

HERE = os.path.dirname(os.path.abspath(__file__))
MAP_FILE = os.path.join(HERE, "media_map.json")
MEDIA = json.load(io.open(MAP_FILE, encoding="utf-8")) if os.path.isfile(MAP_FILE) else {}

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
      if(!video.dataset.fallback && (video.currentSrc || video.src).indexOf("media.doubao.com") >= 0){
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

OLD_VIDEO_TIMEOUT = "    setTimeout(go, 6000);"

NEW_VIDEO_TIMEOUT = """    setTimeout(function(){
      if(!started && !video.dataset.fallback && (video.currentSrc || video.src).indexOf("media.doubao.com") >= 0){
        video.dataset.fallback = "1";
        video.src = "assets/" + url.split("/").pop();
        video.load();
        return;
      }
      go();
    }, 8000);"""

HTML = "index.html"
html = io.open(HTML, encoding="utf-8").read()
out = html

# 1) 远端素材 → media.doubao.com 长期直链
if MEDIA:
    out = re.sub(re.escape(CDN) + r"([A-Za-z0-9._-]+\.(?:webp|jpg|jpeg|png|mp4))",
                 lambda m: MEDIA.get(m.group(1), CDN + m.group(1)), out)

# 2) 修补历史遗留的未闭合 img 标签
out = re.sub(r'(onerror="this\.onerror=null;this\.src=\'[^\']*\'")(?!\s*>)', r'\1>', out)


# 3) 给远程 img 补一次性回落
def _img_fb(m):
    tag = m.group(0)
    if "onerror" in tag:
        return tag
    sm = re.search(r'src="([^"]+)"', tag)
    if not sm or not sm.group(1).startswith("http"):
        return tag
    return tag[:-1] + " onerror=\"this.onerror=null;this.src='assets/%s'\">" % sm.group(1).rsplit("/", 1)[-1]


out = re.sub(r"<img [^>]*>", _img_fb, out)

# 4) 图片弹层大图补回落（去掉空的初始 src，避免误触发）
if 'id="modalImg" src=""' in out and "getAttribute('src')" not in out:
    out = out.replace(
        '<img id="modalImg" src="" alt="作品大图">',
        '<img id="modalImg" alt="作品大图" '
        'onerror="this.onerror=null;this.src=\'assets/\'+(this.getAttribute(\'src\')||\'\').split(\'/\').pop()">')

# 5) 视频：错误与慢网兜底
if OLD_VIDEO_ERROR in out:
    out = out.replace(OLD_VIDEO_ERROR, NEW_VIDEO_ERROR)
    print("video fallback handler patched")

if OLD_VIDEO_TIMEOUT in out:
    out = out.replace(OLD_VIDEO_TIMEOUT, NEW_VIDEO_TIMEOUT)
    print("video slow-network switch patched")

out = out.replace('indexOf("raw.githubusercontent.com")', 'indexOf("media.doubao.com")')


# 6) 统一 TRACK 编号
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

print("media.doubao refs:", out.count("media.doubao.com"))
print("raw cdn refs:", out.count(CDN))
print("img fallbacks:", out.count("this.onerror=null"))
print("track markers:", re.findall(r"TRACK \d+", out))
