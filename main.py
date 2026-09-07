"""
astrbot_plugin_Identity_V - 第五人格群聊Bot插件
"""

import importlib.util
import os
from pathlib import Path

from astrbot.api import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register

PLUGIN_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = PLUGIN_DIR / "src"

COMMAND_DIRS: dict[str, str] = {
    "学姐桃": "学姐桃",
    "角色": "角色查询",
}

HANDLER_FILE = "handler.py"


def _load_handler(folder: str):
    handler_path = SRC_DIR / folder / HANDLER_FILE
    if not handler_path.is_file():
        logger.warning(f"Identity-V: 命令文件夹 src/{folder}/ 缺少 {HANDLER_FILE}")
        return None
    module_name = f"identity_v_{folder}_handler"
    spec = importlib.util.spec_from_file_location(module_name, handler_path)
    if spec is None or spec.loader is None:
        logger.error(f"Identity-V: 无法为 {folder}/{HANDLER_FILE} 创建模块 spec")
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        logger.error(f"Identity-V: 加载 {folder}/{HANDLER_FILE} 失败: {e}")
        return None
    return module


@register(
    "astrbot_plugin_Identity_V",
    "orpnq",
    "带有第五人格特色的群聊Bot插件",
    "v1.0.0",
    "https://github.com/orpnq/astrbot_plugin_Identity-V",
)
class Main(Star):

    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("Identity-V 插件已加载！")

    @filter.command("学姐桃")
    async def xuejietao(self, event: AstrMessageEvent):
        """发送学姐桃图片"""
        async for item in self._dispatch(event, COMMAND_DIRS["学姐桃"]):
            yield item

    @filter.command("角色")
    async def role(self, event: AstrMessageEvent):
        """返回第五人格WIKI角色页面链接"""
        async for item in self._dispatch(event, COMMAND_DIRS["角色"]):
            yield item

    async def _dispatch(self, event: AstrMessageEvent, folder: str):
        module = _load_handler(folder)
        if module is None:
            yield event.plain_result(f"指令执行文件缺失: 请在插件 {folder}/ 目录下放置 {HANDLER_FILE}")
            return
        handler = getattr(module, "handle", None)
        if handler is None:
            yield event.plain_result(f"指令执行文件格式错误: {folder}/{HANDLER_FILE} 缺少 handle(event) 函数")
            return
        try:
            result = handler(event)
            if hasattr(result, "__aiter__"):
                async for item in result:
                    if isinstance(item, str):
                        yield event.plain_result(item)
                    elif isinstance(item, bytes):
                        yield event.chain_result([event.image_result(item)])
                    else:
                        yield item
            else:
                for item in result:
                    if isinstance(item, str):
                        yield event.plain_result(item)
                    elif isinstance(item, bytes):
                        yield event.chain_result([event.image_result(item)])
                    else:
                        yield item
        except Exception as e:
            logger.error(f"Identity-V: 执行 {folder}/{HANDLER_FILE} 出错: {e}")
            yield event.plain_result("指令执行出错，请查看插件日志。")