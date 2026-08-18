# -*- coding: utf-8 -*-
"""Extract mermaid blocks from the report markdown into individual .mmd files."""
import os
import re

SRC = os.path.join(os.path.dirname(__file__), "智慧园区核心建设模块解析-从技术集成到价值赋能.md")
OUT_DIR = os.path.join(os.path.dirname(__file__), ".mermaid-tool", "blocks")

os.makedirs(OUT_DIR, exist_ok=True)

with open(SRC, 'r', encoding='utf-8') as f:
    lines = f.readlines()

blocks = []
current = None
for line in lines:
    if line.strip().startswith('```mermaid'):
        current = []
    elif line.strip().startswith('```') and current is not None:
        blocks.append('\n'.join(current))
        current = None
    elif current is not None:
        current.append(line.rstrip('\n'))

print(f"提取到 {len(blocks)} 个 mermaid 块")
for i, block in enumerate(blocks, 1):
    path = os.path.join(OUT_DIR, f"fig{i:02d}.mmd")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(block)
    print(f"  fig{i:02d}.mmd ({len(block.splitlines())} 行)")
