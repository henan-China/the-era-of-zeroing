#!/usr/bin/env python3
"""自动归位图片 + 生成素材清单（供 GitHub Actions 调用）
1) 把仓库根目录的图片自动移动到 assets/（成员传错位置也能自动修复）
2) 扫描 assets/ 全部图片，生成 assets-manifest.json（页面据此自动展示）
"""
import os, json, subprocess

EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
ROOT = 'assets'
os.makedirs(ROOT, exist_ok=True)

moved = []
for f in sorted(os.listdir('.')):
    if f.lower().endswith(EXTS) and os.path.isfile(f):
        # 用 git mv 保留历史（工作区移动即可，后续统一 git add）
        try:
            subprocess.run(['git', 'mv', f, os.path.join(ROOT, f)], check=True)
            moved.append(f)
        except subprocess.CalledProcessError:
            subprocess.run(['mv', f, os.path.join(ROOT, f)], check=True)
            moved.append(f + ' (plain mv)')

manifest = []
for f in sorted(os.listdir(ROOT)):
    if f.lower().endswith(EXTS):
        p = os.path.join(ROOT, f)
        try:
            h = subprocess.check_output(['git', 'hash-object', p]).decode().strip()
        except Exception:
            h = '?'
        manifest.append({'file': f, 'hash': h})

with open('assets-manifest.json', 'w', encoding='utf-8') as fp:
    json.dump(manifest, fp, ensure_ascii=False, indent=1)

print('moved:', moved if moved else 'none')
print('manifest items:', len(manifest))
