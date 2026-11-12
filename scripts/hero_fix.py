#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hero 补丁：丝线锚点校准到实测指尖、人偶落点与丝线解耦、入场时长压缩、首屏资源优先级。
幂等：已打过的位置会跳过，可重复执行。
由 .github/workflows/sync-media.yml 在推送后运行，直接改写仓库根目录 index.html。
"""
import pathlib

T = pathlib.Path(__file__).resolve().parent.parent / "index.html"

PRE = "https://media.doubao.com/space/api/box/stream/download/all_by_mount_point/"
HERO = ["Gr8PbAuqposqmfx3koqcQz4Kny3", "NMMSbDWhCo70NOxZVAcc6mdlnDw", "CgFgbHyZzoaPh1xOUHbcAc8pnde",
        "EvHBbUAinogQZcxZU3UcMg4Znnc", "Lj2wb4Fa3oZrOvx5eRxcj35snnf", "IlK8bZ84Sojoy9xtJCzcCGjGn8g"]
STAGE = "LUrVbS7Ygo9EWXxpc5ncZkbYnhS"

FINGER_OLD = ("{fx:0.220, fyv:0.90},\n"
              "    {fx:0.305, fyv:0.87},\n"
              "    {fx:0.672, fyv:0.87},\n"
              "    {fx:0.760, fyv:0.916},\n"
              "    {fx:0.836, fyv:0.826}")
FINGER_NEW = ("{fx:0.369, fyv:0.570},\n"
              "    {fx:0.419, fyv:0.432},\n"
              "    {fx:0.562, fyv:0.440},\n"
              "    {fx:0.639, fyv:0.503},\n"
              "    {fx:0.681, fyv:0.384}")

FIG_OLD = (".hero-fig{\n"
           "  position:absolute;left:50%;top:46%;transform:translateX(-50%);\n"
           "  height:20vh;opacity:0;transition:opacity 1.1s ease .55s;\n"
           "}")
FIG_NEW = (".hero-fig{\n"
           "  position:absolute;left:37%;top:68%;transform:translateX(-50%);\n"
           "  height:20vh;opacity:0;transition:opacity .55s ease .2s;\n"
           "}\n"
           "/* 五个人偶的默认落点：JS 未介入（减少动效 / 首帧）时也不会叠在一起 */\n"
           ".hero-fig:nth-child(1){left:37%}\n"
           ".hero-fig:nth-child(2){left:43.5%}\n"
           ".hero-fig:nth-child(3){left:50%}\n"
           ".hero-fig:nth-child(4){left:56.5%}\n"
           ".hero-fig:nth-child(5){left:63%}")

PATH_OLD = ('      <path class="ss" d="M27.1 43.9 C 29.5 45, 31 45.9, 37 46.5"/>\n'
            '      <path class="ss" d="M41 43.9 C 43 45, 44 45.9, 43.5 46.5"/>\n'
            '      <path class="ss" d="M50 35.3 C 51.6 40, 52.3 44, 50 46.5"/>\n'
            '      <path class="ss" d="M59 43.9 C 60.5 45, 61 45.9, 56.5 46.5"/>\n'
            '      <path class="ss" d="M72.9 43.9 C 74 45, 75 45.9, 63 46.5"/>')
PATH_NEW = ('      <path class="ss" d="M37.7 28.5 C 38.6 44, 37.3 58, 37 68"/>\n'
            '      <path class="ss" d="M42.3 21.6 C 42.2 38, 43.1 55, 43.5 68"/>\n'
            '      <path class="ss" d="M55.8 22 C 54.6 38, 50.9 55, 50 68"/>\n'
            '      <path class="ss" d="M63.1 25.2 C 62.4 40, 57.6 56, 56.5 68"/>\n'
            '      <path class="ss" d="M67 19.2 C 66.2 36, 64 55, 63 68"/>')

DOT_OLD = ('    <span class="string-dot" style="left:37%;top:46%"></span>\n'
           '    <span class="string-dot" style="left:43.5%;top:46%"></span>\n'
           '    <span class="string-dot" style="left:50%;top:46%"></span>\n'
           '    <span class="string-dot" style="left:56.5%;top:46%"></span>\n'
           '    <span class="string-dot" style="left:63%;top:46%"></span>')
DOT_NEW = ('    <span class="string-dot" style="left:37%;top:68%"></span>\n'
           '    <span class="string-dot" style="left:43.5%;top:68%"></span>\n'
           '    <span class="string-dot" style="left:50%;top:68%"></span>\n'
           '    <span class="string-dot" style="left:56.5%;top:68%"></span>\n'
           '    <span class="string-dot" style="left:63%;top:68%"></span>')

EASE_OLD = ("var fs = figState[i];\n"
            "        fs.x += (ex - fs.x) * .10;\n"
            "        fs.y += (ey - fs.y) * .10;")
EASE_NEW = ("// 首帧直接落在目标位（避免开场五个人偶叠在画面中央再散开）\n"
            "        var fs = figState[i];\n"
            "        if(fs.x === null){ fs.x = ex; fs.y = ey; }\n"
            "        else { fs.x += (ex - fs.x) * .10; fs.y += (ey - fs.y) * .10; }")

FONT_OLD = ('<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2'
            '?family=Noto+Serif+SC:wght@600;700&amp;family=Noto+Sans+SC:wght@400;500&amp;display=swap">')
FONT_NEW = ('<link rel="preload" as="style" href="https://miaoda.feishu.cn/fonts/css2'
            '?family=Noto+Serif+SC:wght@600;700&amp;family=Noto+Sans+SC:wght@400;500&amp;display=swap"'
            ' onload="this.rel=\'stylesheet\'">\n'
            '<noscript><link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2'
            '?family=Noto+Serif+SC:wght@600;700&amp;family=Noto+Sans+SC:wght@400;500&amp;display=swap"></noscript>')

PC_OLD = '<link rel="preconnect" href="https://p3-flow-sign.byteimg.com" crossorigin>'
PC_NEW = PC_OLD + '\n<link rel="preconnect" href="https://media.doubao.com" crossorigin>'

PRELOADS = ('<!-- 首屏 Hero 素材预加载 -->\n'
            '<link rel="preload" as="image" href="' + PRE + STAGE + '">\n' +
            '\n'.join('<link rel="preload" as="image" href="%s%s"%s>'
                      % (PRE, pid, ' fetchpriority="high"' if i == 0 else '')
                      for i, pid in enumerate(HERO)))

WHITE_URL = "https://aka.doubaocdn.com/s/DQHb26kgbw"
WHITE_ASSET = "assets/hero-hands-white.webp"

# 预加载块前移到 <head> 顶部（紧跟字体块），让图片在解析 40KB 内联样式前就开始下载
TOPBLOCK = ('<link rel="preload" as="image" href="' + PRE + STAGE + '">\n'
            '<!-- 首屏六张 Hero 素材提前并发拉取，不等 body 解析完 -->\n' +
            '\n'.join('<link rel="preload" as="image" href="%s" fetchpriority="high">' % WHITE_URL
                      if i == 0 else
                      '<link rel="preload" as="image" href="%s%s">' % (PRE, pid)
                      for i, pid in enumerate(HERO)))
NOSCRIPT = ('<noscript><link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2'
            '?family=Noto+Serif+SC:wght@600;700&amp;family=Noto+Sans+SC:wght@400;500&amp;display=swap"></noscript>')

PAIRS = [
    ("指尖锚点", FINGER_OLD, FINGER_NEW),
    ("人偶 CSS 落点", FIG_OLD, FIG_NEW),
    ("双手淡入时长", "opacity:0;transition:opacity 1.1s ease .35s;", "opacity:0;transition:opacity .5s ease .1s;"),
    ("丝线淡入时长", "opacity:0;transition:opacity 1s ease;",
     "opacity:0;transition:opacity .5s ease;transition-delay:.15s;"),
    ("静态丝线", PATH_OLD, PATH_NEW),
    ("丝线端点", DOT_OLD, DOT_NEW),
    ("人偶落点数组", "var hm = {topPct:1, wPct:80, hPct:45};",
     "var hm = {topPct:1, wPct:80, hPct:45};\n"
     "  // 五个人偶的落点（画面宽度百分比）：与指尖解耦，保持均分间距\n"
     "  var endBase = [37, 43.5, 50, 56.5, 63];"),
    ("丝线终点", "var ex = sx + w3 + act * (curXPct - sx) * .18;",
     "var ex = endBase[i] + w3 * .6 + act * (curXPct - endBase[i]) * .18;"),
    ("悬挂高度", "// 丝线长度：以手办高度为基准 1.6 倍（随视口/手办增大而变长，大屏不再显短），上限保证角色不出屏\n"
     "        var eyBase = sy + fhNow * 1.6;",
     "// 手办悬挂高度：与指尖解耦，脚下落在舞台下沿（任何窗口尺寸一致）\n"
     "        var eyBase = 90 - fhNow * 1.1;\n"
     "        if(eyBase < sy + 12){ eyBase = sy + 12; }"),
    ("首帧落位", "figState.push({x:50, y:46, r:0})", "figState.push({x:null, y:null, r:0})"),
    ("落位缓动", EASE_OLD, EASE_NEW),
    ("粒子数量", "var pCount = window.innerWidth < 768 ? 55 : 110;",
     "var pCount = window.innerWidth < 768 ? 26 : 54;"),
    ("字体非阻塞", FONT_OLD, FONT_NEW),
    ("media 预连接", PC_OLD, PC_NEW),
    ("字体预连接", '<link rel="preconnect" href="https://miaoda.feishu.cn">',
     '<link rel="preconnect" href="https://miaoda.feishu.cn" crossorigin>'),
]

# ===== 白模双手（white model hands v6）替换 =====
IMG_OLD = ('      <img src="%s%s" alt="操控丝线的双手模型" '
           'onerror="this.onerror=null;this.src=\'assets/hero-hands.webp\'">'
           % (PRE, HERO[0]))
IMG_NEW = ('      <img src="%s" alt="操控丝线的双手模型" '
           'onerror="this.onerror=null;this.src=\'%s\'">' % (WHITE_URL, WHITE_ASSET))

PRELOAD_OLD = '<link rel="preload" as="image" href="%s%s" fetchpriority="high">' % (PRE, HERO[0])
PRELOAD_NEW = '<link rel="preload" as="image" href="%s" fetchpriority="high">' % WHITE_URL

WRAP_OLD = ("  position:absolute;top:0;left:50%;transform:translateX(-50%);\n"
            "  width:min(1320px,94%);z-index:4;pointer-events:none;")
WRAP_NEW = ("  position:absolute;top:1%;left:50%;transform:translateX(-50%);\n"
            "  width:min(1080px,76%);z-index:4;pointer-events:none;")

FILTER_OLD = "filter:drop-shadow(0 26px 50px rgba(0,0,0,.5))"
FILTER_NEW = "filter:brightness(.88) saturate(.72) drop-shadow(0 26px 50px rgba(0,0,0,.5))"

M900_OLD = "  .hands-wrap{top:0;width:108%}"
M900_NEW = "  .hands-wrap{top:2%;width:104%}"
M520_OLD = "  .hands-wrap{top:0;width:112%}"
M520_NEW = "  .hands-wrap{top:3%;width:108%}"

PATH2_NEW = ('      <path class="ss" d="M28.3 34.4 C 28.3 48.5, 28.3 60.6, 37 68"/>\n'
             '      <path class="ss" d="M35.0 33.3 C 35.0 47.9, 35.0 60.4, 43.5 68"/>\n'
             '      <path class="ss" d="M50.2 27.0 C 50.2 44.2, 50.2 59.0, 50 68"/>\n'
             '      <path class="ss" d="M63.1 33.3 C 63.1 47.9, 63.1 60.4, 56.5 68"/>\n'
             '      <path class="ss" d="M70.1 35.0 C 70.1 48.8, 70.1 60.7, 63 68"/>')

FINGER2_OLD = "  var fingerBase = [\n    " + FINGER_NEW + "\n  ];"
FINGER2_NEW = ("  // 按 white model hands v6（3127×1340）实测指尖坐标标定，丝线起点贴合指尖\n"
               "  var fingerBase = [\n"
               "    {fx:0.214, fyv:0.902},\n"
               "    {fx:0.303, fyv:0.871},\n"
               "    {fx:0.503, fyv:0.700},\n"
               "    {fx:0.673, fyv:0.871},\n"
               "    {fx:0.765, fyv:0.916}\n"
               "  ];")

HM_OLD = "  var hm = {topPct:1, wPct:80, hPct:45};"
HM_NEW = "  var hm = {topPct:1, wPct:76, hPct:37};"

METRICS_OLD = ("  function updateHandMetrics(){\n"
               "    if(!handsWrap) return;\n"
               "    var r = handsWrap.getBoundingClientRect();\n"
               "    var hr = hero.getBoundingClientRect();\n"
               "    // 用 Hero 内相对坐标：页面滚动时丝线长度与位置保持不变\n"
               "    hm.topPct = (r.top - hr.top) / window.innerHeight * 100;\n"
               "    hm.wPct = r.width / window.innerWidth * 100;\n"
               "    hm.hPct = r.height / window.innerHeight * 100;\n"
               "  }")
METRICS_NEW = ("  function updateHandMetrics(){\n"
               "    if(!handsWrap) return;\n"
               "    var r = handsWrap.getBoundingClientRect();\n"
               "    var hr = hero.getBoundingClientRect();\n"
               "    var iw = window.innerWidth || document.documentElement.clientWidth || 0;\n"
               "    var ih = window.innerHeight || document.documentElement.clientHeight || 0;\n"
               "    // 图片未就绪（宽/高为 0）时保留上一帧几何，避免首帧算出无效坐标\n"
               "    if(!isFinite(r.width) || !isFinite(r.height) || r.width < 1 || r.height < 1 || iw < 1 || ih < 1) return;\n"
               "    // 用 Hero 内相对坐标：页面滚动时丝线长度与位置保持不变\n"
               "    hm.topPct = (r.top - hr.top) / ih * 100;\n"
               "    hm.wPct = r.width / iw * 100;\n"
               "    hm.hPct = r.height / ih * 100;\n"
               "  }")

SY_OLD = "        var sy = hm.topPct + hm.hPct * b.fyv;"
SY_NEW = ("        var sy = hm.topPct + hm.hPct * b.fyv;\n"
          "        if(!isFinite(sy)){ sy = hm.topPct; }")

EX2_OLD = "        var ex = endBase[i] + w3 * .6 + act * (curXPct - endBase[i]) * .18;"
EX2_NEW = ("        var ex = endBase[i] + w3 * .6 + act * (curXPct - endBase[i]) * .18;\n"
           "        if(!isFinite(ex)) ex = endBase[i];")

FS_OLD = "        if(fs.x === null){ fs.x = ex; fs.y = ey; }"
FS_NEW = "        if(fs.x === null || !isFinite(fs.x) || !isFinite(fs.y)){ fs.x = ex; fs.y = ey; }"

CURVE_OLD = ('          " C " + (sx + w1).toFixed(2) + " " + c1y.toFixed(2) +\n'
             '          ", " + (sx + w2).toFixed(2) + " " + c2y.toFixed(2) +')
CURVE_NEW = ('          " C " + (sx + w1 + (fs.x - sx) * .22).toFixed(2) + " " + c1y.toFixed(2) +\n'
             '          ", " + (sx + w2 + (fs.x - sx) * .55).toFixed(2) + " " + c2y.toFixed(2) +')

WHITE_PAIRS = [
    ("白模双手 img", IMG_OLD, IMG_NEW),
    ("白模双手预加载", PRELOAD_OLD, PRELOAD_NEW),
    ("双手容器尺寸", WRAP_OLD, WRAP_NEW),
    ("双手滤镜", FILTER_OLD, FILTER_NEW),
    ("移动端双手 900", M900_OLD, M900_NEW),
    ("移动端双手 520", M520_OLD, M520_NEW),
    ("静态丝线（白模坐标）", PATH_NEW, PATH2_NEW),
    ("指尖锚点（白模）", FINGER2_OLD, FINGER2_NEW),
    ("几何默认值", HM_OLD, HM_NEW),
    ("几何测量防抖", METRICS_OLD, METRICS_NEW),
    ("丝线起点兜底", SY_OLD, SY_NEW),
    ("终点兜底", EX2_OLD, EX2_NEW),
    ("人偶状态兜底", FS_OLD, FS_NEW),
    ("丝线弧度", CURVE_OLD, CURVE_NEW),
]


def ensure_asset():
    """把白模双手素材落到仓库 assets/（aka 短链失效时页面仍有本地兜底）。
    已存在则跳过；下载失败不影响 html 补丁。"""
    path = T.parent / WHITE_ASSET
    if path.exists() and path.stat().st_size > 1000:
        print("asset: 已存在，跳过")
        return
    try:
        import urllib.request
        with urllib.request.urlopen(WHITE_URL, timeout=30) as r:
            data = r.read()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print("asset: 已下载 %d bytes" % len(data))
    except Exception as e:
        print("asset: 下载失败（保留 aka 直链）", e)


def move_preloads(text):
    """把首屏预加载块从 </head> 前移到字体块之后（更早发现、更早下载）。幂等。"""
    if TOPBLOCK in text:
        return text
    marker = "<!-- 首屏 Hero 素材预加载 -->\n"
    if marker in text:
        i = text.index(marker)
        j = text.index("</head>", i)
        text = text[:i] + text[j:]
    if NOSCRIPT in text:
        text = text.replace(NOSCRIPT, NOSCRIPT + "\n" + TOPBLOCK, 1)
    else:
        text = text.replace("</head>", TOPBLOCK + "\n</head>", 1)
    return text


def main():
    if not T.exists():
        raise SystemExit("找不到 index.html")
    text = T.read_text(encoding="utf-8")
    applied, skipped = [], []
    for label, old, new in PAIRS + WHITE_PAIRS:
        if new in text:
            skipped.append(label)
            continue
        if old not in text:
            skipped.append(label + "(未命中)")
            continue
        text = text.replace(old, new, 1)
        applied.append(label)
    before = text
    text = move_preloads(text)
    if text != before:
        applied.append("预加载前移")
    # 预加载行可能同时存在于 head 与 body 两处，统一改写（幂等）
    if PRELOAD_OLD in text:
        text = text.replace(PRELOAD_OLD, PRELOAD_NEW)
        applied.append("预加载行统一")
    T.write_text(text, encoding="utf-8")
    ensure_asset()
    print("applied:", ", ".join(applied) or "无")
    print("skipped:", ", ".join(skipped) or "无")


if __name__ == "__main__":
    main()
