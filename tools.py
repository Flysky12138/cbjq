import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from typing import Any, Dict, Optional, Tuple

import cv2
import mss
import numpy as np
import pygetwindow as gw
from cv2.typing import MatLike
from PIL import Image


def get_window_rect(title: str) -> Dict[str, int]:
    """获取指定窗口的坐标和大小"""
    windows = gw.getWindowsWithTitle(title)
    if not windows:
        raise Exception(f"找不到标题为 '{title}' 的窗口")

    win = windows[0]
    if win.isMinimized:
        win.restore()

    return {"left": win.left, "top": win.top, "width": win.width, "height": win.height}


def get_window_screenshot_mss(title: Optional[str] = None):
    """获取指定窗口或全屏的截图"""
    with mss.mss() as sct:
        rect = get_window_rect(title) if title else sct.monitors[0]
        img = sct.grab(rect)
        screenshot = Image.frombytes("RGB", img.size, img.rgb)
    return screenshot


def crop_screenshot(screenshot: Image.Image, margin: Optional[Tuple[int, int, int, int]] = None):
    """根据 CSS 风格的 margin 裁剪图像"""
    if margin:
        top, right, bottom, left = margin
        width, height = screenshot.size
        box = (left, top, width - right, height - bottom)
        return screenshot.crop(box)
    return screenshot


def match_templates(screenshot: Image.Image, template: MatLike, threshold=0.9):
    """在截图中查找模板图像"""
    screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(screenshot_np, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        x, y = max_loc
        return x + 5, y + 5
    return None


class Match:
    def __init__(self) -> None:
        self.events: dict[str, Any] = {}
        self.templates: dict[str, MatLike] = {}
        self.margin: dict[str, Optional[Tuple[int, int, int, int]]] = {}

    def template_path(self, path: str, margin: Optional[Tuple[int, int, int, int]] = None):
        """自定义装饰器，记录图片模板和对应事件"""

        def decorator(func):
            self.events[path] = func
            self.templates[path] = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            self.margin[path] = margin

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def thread_run(self, max_workers: int = 4):
        """多线程执行图片匹配"""
        executor = ThreadPoolExecutor(max_workers)
        lock = threading.Lock()
        screenshot = get_window_screenshot_mss()

        futures = {
            executor.submit(match_templates, crop_screenshot(screenshot, self.margin.get(path)), template): path for path, template in self.templates.items()
        }

        for future in as_completed(futures):
            result = future.result()
            if result:
                with lock:
                    path = futures[future]
                    margin = self.margin.get(path)
                    x, y = result
                    if margin:
                        x += margin[3]
                        y += margin[0]
                    self.events[path]((x, y))  # 调用事件函数，传入匹配到的坐标
                break
