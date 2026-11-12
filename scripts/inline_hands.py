#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Hero 白模双手内联成 data URI，并收敛首屏图片预加载块：彻底去掉会过期的外链依赖。
原因：aka.doubaocdn.com 分享短链约 7-8 天整批过期；GitHub Pages 直连素材在国内约 2KB/s。
源图仍是仓库里的 assets/hero-hands-white.webp（由 hero_fix.py 落盘），本脚本只改 index.html。
幂等：重建规则是确定的——每次把 head 内的图片预加载行全部收掉再按原顺序重写一块。
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
T = ROOT / "index.html"
ASSET = ROOT / "assets" / "hero-hands-white.webp"

PREFIX = "https://media.doubao.com/space/api/box/stream/download/all_by_mount_point/"
STAGE_ID = "LUrVbS7Ygo9EWXxpc5ncZkbYnhS"
STAGE_FILE = next((ROOT / "assets" / "media").glob(STAGE_ID + ".*"), None)
IMG_RE = re.compile(r'(<img src=")([^"]*)(" alt="操控丝线的双手模型")')
PRELOAD_RE = re.compile(r'\n?<link rel="preload" as="image" href="([^"]+)"[^>]*>')
# 预加载块注释（两种措辞都用正则收，避免逐字比对漏掉造成累积）
COMMENT_RE = re.compile(r'\n?<!--[^\n]*首屏[^\n]*Hero[^\n]*-->')


def main():
    if not T.exists():
        raise SystemExit("找不到 index.html")
    if not ASSET.exists():
        print("inline: 缺少 assets/hero-hands-white.webp，跳过")
        return
    uri = "data:image/webp;base64," + base64.b64encode(ASSET.read_bytes()).decode("ascii")
    orig = T.read_text(encoding="utf-8")

    head_end = orig.find("</head>")
    if head_end < 0:
        raise SystemExit("index.html 里找不到 </head>")
    head, tail = orig[:head_end], orig[head_end:]

    # 1) 收集现有图片预加载 URL（保持原有顺序、去重），剔除已内联的双手外链
    urls = []
    for u in PRELOAD_RE.findall(head):
        if "DQHb26kgbw" in u or u.startswith("data:"):
            continue
        if u not in urls:
            urls.append(u)
    stage = next((u for u in urls if u.endswith(STAGE_ID)), None)
    figs = [u for u in urls if not u.endswith(STAGE_ID)]
    if stage and STAGE_FILE is not None:
        stage = None  # 舞台背景改为内联，不再需要外链预加载

    # 2) 收掉所有图片预加载行与块注释
    head = PRELOAD_RE.sub("", head)
    head = COMMENT_RE.sub("", head)

    # 3) 重建唯一一块预加载（stage 在前，其余按原顺序）
    block = ""
    if stage:
        block += '<link rel="preload" as="image" href="%s">\n' % stage
    if figs:
        block += "<!-- 首屏 Hero 素材提前并发拉取，不等 body 解析完 -->\n"
        block += "".join('<link rel="preload" as="image" href="%s">\n' % u for u in figs)
    if block:
        m = re.search(r'<noscript><link rel="stylesheet"[^>]*></noscript>\n', head)
        if m:
            head = head[:m.end()] + block + head[m.end():]
        else:
            head = head.rstrip("\n") + "\n" + block

    text = head + tail

    # 4) hands 图片内联
    def swap(m):
        if m.group(2) == uri:
            return m.group(0)
        return m.group(1) + uri + m.group(3)

    text = IMG_RE.sub(swap, text)

    # 5) 舞台背景（CSS background）也内联，避免成为唯一没有兜底的外链图片
    stage_note = "背景外链"
    if STAGE_FILE is not None and STAGE_FILE.stat().st_size > 0:
        mime = {"webp": "image/webp", "jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png"}.get(STAGE_FILE.suffix.lstrip(".").lower(), "image/webp")
        suri = "data:%s;base64,%s" % (mime, base64.b64encode(STAGE_FILE.read_bytes()).decode("ascii"))
        pat = re.compile(r"url\((['\"]?)" + re.escape(PREFIX + STAGE_ID) + r"\1\)")
        text, n = pat.subn("url(%s)" % suri, text)
        stage_note = "背景内联" if n else "背景未命中"

    if text == orig:
        print("inline: 已内联，跳过")
        return
    T.write_text(text, encoding="utf-8")
    print("inline: 素材 %d bytes；index.html %d → %d 字节；预加载 %d 条；%s"
          % (len(ASSET.read_bytes()), len(orig.encode("utf-8")), len(text.encode("utf-8")),
             (1 if stage else 0) + len(figs), stage_note))


if __name__ == "__main__":
    main()
