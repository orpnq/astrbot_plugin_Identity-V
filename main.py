"""
astrbot_plugin_Identity_V - 第五人格群聊Bot插件

每个命令对应 src/ 下的一个子文件夹，子文件夹内放置 handler.py 和资源文件。
main.py 只负责：注册命令 -> 动态加载对应子文件夹的 handler.py。
"""

import base64
import importlib.util
import os
from pathlib import Path
from typing import AsyncIterator

from astrbot.api import logger
from astrbot.api.event import filter, AstrMessageEvent, MessageChain
from astrbot.api.star import Context, Star, register

# 插件自身目录
PLUGIN_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = PLUGIN_DIR / "src"

# 命令映射：指令名 -> 文件夹名
COMMAND_DIRS: dict[str, str] = {
    "学姐桃": "学姐桃",
}

HANDLER_FILE = "handler.py"
_MODULE_PREFIX = "identity_v_plugin"


def _load_handler(folder: str):
    """动态加载 src/<folder>/handler.py"""
    handler_path = SRC_DIR / folder / HANDLER_FILE
    if not handler_path.is_file():
        logger.warning(f"Identity-V: 命令文件夹 src/{folder}/ 缺少 {HANDLER_FILE}")
        return None
    module_name = f"{_MODULE_PREFIX}_{folder}_handler"
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


async def _iter_results(result) -> AsyncIterator:
    """将 handle() 的返回值统一规整为异步迭代器"""
    if hasattr(result, "__aiter__"):
        async for item in result:
            yield item
        return
    if hasattr(result, "__iter__") and not hasattr(result, "__await__"):
        for item in result:
            yield item
        return
    awaited = await result
    if hasattr(awaited, "__aiter__"):
        async for item in awaited:
            yield item
    elif hasattr(awaited, "__iter__"):
        for item in awaited:
            yield item


@register(
    "astrbot_plugin_Identity_V",
    "orpnq",
    "带有第五人格特色的群聊Bot插件",
    "v1.0.0",
    "https://github.com/orpnq/astrbot_plugin_Identity-V",
)
class Main(Star):
    """第五人格插件主类：只负责命令注册与调度"""

    def __init__(self, context: Context):
        super().__init__(context)
        logger.info("Identity-V 插件已加载！")

    @filter.command("学姐桃")
    async def xuejietao(self, event: AstrMessageEvent):
        """发送学姐桃图片"""
        async for item in self._dispatch(event, COMMAND_DIRS["学姐桃"]):
            yield item

    async def _dispatch(self, event: AstrMessageEvent, folder: str):
        """加载命令文件夹的 handler.py，将产出的内容合并为消息链发送"""
        module = _load_handler(folder)
        if module is None:
            yield event.plain_result(
                f"指令执行文件缺失: 请在插件 {folder}/ 目录下放置 {HANDLER_FILE} 后重载插件。"
            )
            return
        handler = getattr(module, "handle", None)
        if handler is None:
            yield event.plain_result(
                f"指令执行文件格式错误: {folder}/{HANDLER_FILE} 缺少 handle(event) 函数。"
            )
            return
        try:
            chain = MessageChain()
            has_content = False
            result = handler(event)
            async for item in _iter_results(result):
                if isinstance(item, bytes):
                    chain.base64_image(base64.b64encode(item).decode("utf-8"))
                    has_content = True
                elif isinstance(item, str):
                    chain.message(item)
                    has_content = True
                else:
                    logger.warning(
                        f"Identity-V: {folder}/handler.py 返回了不支持的类型 {type(item).__name__}, 已跳过"
                    )
            if has_content:
                yield event.chain_result(chain.chain)
            else:
                yield event.plain_result(
                    f"指令未产出任何内容: 请检查插件 {folder}/ 目录下的 {HANDLER_FILE}。"
                )
        except Exception as e:
            logger.error(f"Identity-V: 执行 {folder}/{HANDLER_FILE} 出错: {e}")
            yield event.plain_result("指令执行出错，请查看插件日志。")