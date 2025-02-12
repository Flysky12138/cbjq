import os
import time
import keyboard
import pyautogui
import pygetwindow as gw


GAME_WINDOW_TITLE = "尘白禁区"
HOTKEY_TOGGLE = "F2"


SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

# 设置 locateOnScreen 没找到图片不抛出错误
pyautogui.useImageNotFoundException(False)


def toggle_pause():
    global paused
    paused = not paused
    print("暂停中..." if paused else "继续执行")


# 监听按键 F2 进行暂停/继续
paused = True
keyboard.add_hotkey(HOTKEY_TOGGLE, toggle_pause)


def get_window_position():
    """获取窗口位置"""
    window = gw.getWindowsWithTitle(GAME_WINDOW_TITLE)[0]
    return window.left, window.top, window.width, window.height


def select_buff():
    """buff"""
    submit_box = pyautogui.locateOnScreen(os.path.join(SCRIPT_PATH, "./submit.png"), confidence=0.8)
    if not submit_box:
        return
    x, y, width, height = get_window_position()
    pyautogui.click(x + width / 2, y + height / 2)  # 选择 buff
    pyautogui.moveTo(submit_box)
    pyautogui.click()  # 点击 “确认”
    pyautogui.sleep(0.5)
    attack()
    drop_box = pyautogui.locateOnScreen(os.path.join(SCRIPT_PATH, "./drop.png"), confidence=0.8)
    if not drop_box:
        return
    pyautogui.moveTo(drop_box)
    pyautogui.click()  # 点击 “丢弃”
    pyautogui.sleep(1)
    drop_ok_box = pyautogui.locateOnScreen(os.path.join(SCRIPT_PATH, "./drop-ok.png"), confidence=0.8)
    if not drop_ok_box:
        return
    pyautogui.moveTo(drop_ok_box)
    pyautogui.click()


def start():
    """开始"""
    level_box = pyautogui.locateOnScreen(os.path.join(SCRIPT_PATH, "./level.png"))
    if not level_box:
        return
    pyautogui.moveTo(level_box)
    pyautogui.click()
    pyautogui.sleep(1.5)
    level_box = pyautogui.locateOnScreen(os.path.join(SCRIPT_PATH, "./level.png"))
    if level_box:
        window = gw.getWindowsWithTitle(GAME_WINDOW_TITLE)[0]
        window.close()
        exit()
    start_box = pyautogui.locateOnScreen(os.path.join(SCRIPT_PATH, "./start.png"), confidence=0.8)
    if not start_box:
        return
    pyautogui.moveTo(start_box)
    pyautogui.click()
    pyautogui.sleep(8)


def end():
    """退出"""
    end_box = pyautogui.locateOnScreen(os.path.join(SCRIPT_PATH, "./end.png"), confidence=0.8)
    if not end_box:
        return
    pyautogui.moveTo(end_box)
    pyautogui.click()
    pyautogui.sleep(8)


def attack():
    """攻击"""
    attack_box = pyautogui.locateOnScreen(os.path.join(SCRIPT_PATH, "./attack.png"), confidence=0.8)
    if paused or (not attack_box):
        return
    pyautogui.press("e")
    attack()


def main():
    while True:
        if not paused:
            if gw.getActiveWindowTitle() != GAME_WINDOW_TITLE:
                continue
            attack()
            start()
            end()
            select_buff()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
