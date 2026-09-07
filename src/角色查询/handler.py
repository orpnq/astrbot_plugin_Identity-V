"""
角色查询 命令执行文件

负责 /角色名 指令：返回第五人格 BWIKI 角色页面链接。
"""

import urllib.parse

async def handle(event):
    message = event.message_str
    parts = message.strip().split()
    
    if len(parts) < 2:
        yield "请输入角色名，例如：/角色 医生"
        return
    
    role_name = parts[1]
    
    # 将中文角色名进行 URL 编码
    encoded_name = urllib.parse.quote(role_name)
    url = f"https://wiki.biligame.com/dwrg/{encoded_name}"
    
    yield f"🎭 **{role_name}** 的第五人格 WIKI 页面：\n{url}\n（请复制链接到浏览器打开）"