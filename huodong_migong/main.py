import os
import sys
import time

import keyboard
import pyautogui
import pygetwindow as gw

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools import Match, get_window_rect

GAME_WINDOW_TITLE = "尘白禁区"
HOTKEY_TOGGLE = "F2"


def toggle_pause():
    global paused
    paused = not paused
    print("暂停中..." if paused else "继续执行")


# 监听按键 F2 进行暂停/继续
paused = True
keyboard.add_hotkey(HOTKEY_TOGGLE, toggle_pause)


def override_click(*position):
    """自定义点击事件，尘白禁区的点击需要一点延迟才能点击成功"""
    pyautogui.moveTo(*position)
    pyautogui.sleep(0.2)
    pyautogui.click()


match = Match()


@match.template_path("./assets/submit.png")
def submit(point):
    position = get_window_rect(GAME_WINDOW_TITLE)
    override_click(position["left"] + position["width"] / 2, position["top"] + position["height"] / 2)  # 选择 buff
    override_click(point)


@match.template_path("./assets/drop.png")
def drop(point):
    override_click(point)


@match.template_path("./assets/drop-ok.png")
def drop_ok(point):
    override_click(point)


@match.template_path("./assets/level.png", (400, 0, 0, 2700))
def level(point):
    override_click(point)


@match.template_path("./assets/start.png")
def start(point):
    override_click(point)


@match.template_path("./assets/end.png")
def end(point):
    override_click(point)


@match.template_path("./assets/attack.png", (1800, 0, 0, 3000))
def attack(point):
    pyautogui.press("e")
    pyautogui.sleep(2)


def main():
    while True:
        if not paused:
            if gw.getActiveWindowTitle() != GAME_WINDOW_TITLE:
                time.sleep(0.5)
                continue
            match.thread_run(len(match.templates))
        time.sleep(0.1)


if __name__ == "__main__":
    main()
