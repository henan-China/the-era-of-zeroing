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
    ("首屏预加载", "</head>", PRELOADS + "\n</head>"),
]


def main():
    if not T.exists():
        raise SystemExit("找不到 index.html")
    text = T.read_text(encoding="utf-8")
    applied, skipped = [], []
    for label, old, new in PAIRS:
        if new in text:
            skipped.append(label)
            continue
        if text.count(old) != 1:
            skipped.append(label + "(未命中)")
            continue
        text = text.replace(old, new, 1)
        applied.append(label)
    T.write_text(text, encoding="utf-8")
    print("applied:", ", ".join(applied) or "无")
    print("skipped:", ", ".join(skipped) or "无")


if __name__ == "__main__":
    main()
