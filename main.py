import os
import importlib.util
from pathlib import Path
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, register

PLUGIN_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = PLUGIN_DIR / "src"

COMMAND_DIRS = {
    "学姐桃": "学姐桃",
}

def load_handler(folder: str):
    handler_path = SRC_DIR / folder / "handler.py"
    if not handler_path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"{folder}_handler", handler_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

async def dispatch(event: AstrMessageEvent, folder: str):
    module = load_handler(folder)
    if module is None:
        yield event.plain_result(f"指令 {folder} 未配置")
        return
    handler = getattr(module, "handle", None)
    if handler is None:
        yield event.plain_result(f"指令 {folder} 的 handler 缺少 handle 函数")
        return
    async for item in handler(event):
        yield item

@register(
    "astrbot_plugin_Identity-V",
    "orpnq",
    "第五人格群聊Bot插件",
    "v1.0.0"
)
class IdentityVPlugin(Star):
    @filter.command("学姐桃")
    async def xuejietao(self, event: AstrMessageEvent):
        async for item in dispatch(event, COMMAND_DIRS["学姐桃"]):
            yield item