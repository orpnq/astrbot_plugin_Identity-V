import os
from pathlib import Path

IMG_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
IMG_PATH = IMG_DIR / "学姐桃.jpg"

async def handle(event):
    yield "🍑 学姐桃："
    yield IMG_PATH.read_bytes()