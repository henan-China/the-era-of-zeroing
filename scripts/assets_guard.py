#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建期把页面引用的豆包素材快照进 assets/，并注入统一回退。
目的：对象存储直链万一失效（迁移、清理、限流），页面仍能从仓库副本显示，不会白屏。
幂等：已存在的文件跳过；<script id="media-fallback"> 先删后写。
"""
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
T = ROOT / "index.html"
ASSETS = ROOT / "assets"
MEDIA = ASSETS / "media"
PREFIX = "https://media.doubao.com/space/api/box/stream/download/all_by_mount_point/"
MARK_RE = re.compile(r'\n?<script id="media-fallback">.*?</script>\n?', re.S)
IMG_RE = re.compile(r'<img src="(https://media\.doubao\.com/[^"]+)"[^>]*onerror="[^"]*?assets/([^"\'\\ ]+)')
ID_RE = re.compile(r'all_by_mount_point/([A-Za-z0-9]+)')
UA = {"User-Agent": "Mozilla/5.0"}
EXT = {"image/webp": "webp", "image/jpeg": "jpg", "image/png": "png", "video/mp4": "mp4"}
MAX_TOTAL = 60 * 1024 * 1024


def probe_ext(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            return EXT.get((r.headers.get("Content-Type") or "").split(";")[0].strip(), "bin")
    except Exception as e:
        print("probe fail %s: %s" % (url[-24:], type(e).__name__))
        return None


def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=180) as r, open(tmp, "wb") as f:
            while True:
                chunk = r.read(1 << 18)
                if not chunk:
                    break
                f.write(chunk)
        if tmp.stat().st_size == 0:
            tmp.unlink()
            return False
        tmp.replace(dest)
        return True
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        print("download fail %s: %s" % (url[-24:], type(e).__name__))
        return None


def main():
    if not T.exists():
        raise SystemExit("找不到 index.html")
    text = T.read_text(encoding="utf-8")

    # 1) 已声明 onerror 的 <img>：记录的 assets/<name>（按 id 下载后复制过去，避免重复拉取）
    declared = {}
    for url, name in IMG_RE.findall(text):
        m = ID_RE.search(url)
        if m:
            declared.setdefault(m.group(1), name)

    # 2) 逐个 id 下载到 assets/media/<id>.<ext>
    ids = sorted(set(ID_RE.findall(text)))
    mapping = {}
    total = 0
    for i in ids:
        url = PREFIX + i
        dest = next(MEDIA.glob("%s.*" % i), None)
        if dest is None:
            ext = probe_ext(url)
            if not ext:
                continue
            dest = MEDIA / ("%s.%s" % (i, ext))
        if not dest.exists() or dest.stat().st_size == 0:
            if total > MAX_TOTAL:
                print("超出快照预算，跳过 %s" % i)
                continue
            got = fetch(url, dest)
            if got:
                total += dest.stat().st_size
                print("snapshot %s.%s %.0fKB" % (i, dest.suffix.lstrip("."), dest.stat().st_size / 1024))
        mapping[i] = "assets/media/" + dest.name
        name = declared.get(i)
        if name:
            target = ASSETS / name
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(dest.read_bytes())

    # 3) 注入统一回退（捕获阶段，先于各元素自身 onerror）
    body = "{%s}" % ",".join('"%s":"%s"' % (k, v) for k, v in sorted(mapping.items()))
    js = (
        '<script id="media-fallback">\n'
        '(function(){var FB=%s;'
        'document.addEventListener("error",function(e){'
        'var t=e.target;if(!t||!t.tagName)return;'
        'if(t.tagName!=="IMG"&&t.tagName!=="VIDEO")return;'
        'var s=t.currentSrc||t.src||"";var m=s.match(/all_by_mount_point\\/([A-Za-z0-9]+)/);'
        'if(!m||!FB[m[1]])return;'
        'if(t.tagName==="VIDEO"){t.src=FB[m[1]];try{t.load();t.play&&t.play().catch(function(){});}catch(x){}}'
        'else{t.src=FB[m[1]];}'
        '},true);})();\n'
        "</script>\n"
    ) % body

    if "</body>" not in text:
        print("media-fallback: 找不到 </body>，跳过注入")
        T.write_text(text, encoding="utf-8")
        return
    text = MARK_RE.sub("", text)
    text = re.sub(r"\s*</body>", lambda m: "\n" + js + "</body>", text, count=1)
    T.write_text(text, encoding="utf-8")
    print("media-fallback: 快照 %d 个素材（新增 %.1fMB），映射 %d 条"
          % (len(mapping), total / 1048576.0, len(mapping)))


if __name__ == "__main__":
    main()
