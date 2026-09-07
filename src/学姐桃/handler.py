"""
学姐桃 命令执行文件

负责 /学姐桃 指令：发送学姐桃图片。
"""

import os
from pathlib import Path

IMG_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
IMG_PATH = IMG_DIR / "学姐桃.jpg"


async def handle(event):
    """发送标题文本 + 图片"""
    yield "🍑 学姐桃："
    yield IMG_PATH.read_bytes()