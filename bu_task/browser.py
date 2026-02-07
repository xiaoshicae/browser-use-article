"""浏览器启动与连接"""
import os
import socket
import subprocess
import time

from browser_use import BrowserSession
from bu_task.config import settings

# 避免代理影响 CDP 连接
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'


def ensure_chrome() -> bool:
    """确保 Chrome 调试实例已启动，返回是否成功"""
    port = settings.cdp_port
    if _is_port_open(port):
        print(f"✅ Chrome 已在端口 {port} 运行")
        return True

    print("🚀 启动带调试端口的 Chrome...")
    subprocess.Popen(
        [settings.chrome_path, f"--remote-debugging-port={port}",
         f"--user-data-dir={settings.chrome_user_data_dir}",
         "--no-first-run", "--no-default-browser-check",
         "--start-maximized",
         "--hide-crash-restore-bubble",
         "--disable-session-crashed-bubble"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    for i in range(10):
        time.sleep(1)
        if _is_port_open(port):
            print(f"✅ Chrome 已启动（端口 {port}）")
            return True
        print(f"   等待 Chrome 启动... ({i+1}/10)")

    print("❌ Chrome 启动超时")
    return False


def create_session() -> BrowserSession:
    """创建连接到 CDP 的 BrowserSession"""
    return BrowserSession(cdp_url=f"http://localhost:{settings.cdp_port}")


def close_chrome() -> None:
    """关闭通过 CDP 端口启动的 Chrome 实例"""
    port = settings.cdp_port
    if not _is_port_open(port):
        return
    try:
        import signal
        # 通过 CDP 端口找到对应的 Chrome 进程并终止
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"], capture_output=True, text=True
        )
        for pid in result.stdout.strip().splitlines():
            os.kill(int(pid), signal.SIGTERM)
        # 等待端口释放
        for _ in range(5):
            time.sleep(0.5)
            if not _is_port_open(port):
                print("🛑 Chrome 已关闭")
                return
        print("⚠️ Chrome 关闭超时")
    except Exception as e:
        print(f"⚠️ 关闭 Chrome 失败: {e}")


def _is_port_open(port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0
