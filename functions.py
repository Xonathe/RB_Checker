# -*- coding: utf-8 -*-
import os
import time
import design
import autoit
import cv2
import numpy as np
import psutil
import win32gui
import win32process
import win32ui
from PIL import Image
from ctypes import windll
from twilio.rest import Client
from configparser import ConfigParser

data = ConfigParser()
data.read("conf.ini")

SCREENSHOT = Image.Image
process = 'AsteriosGame.exe'
windows = []

account_sid = data.get("Auth", "account_sid")
auth_token = data.get("Auth", "auth_token")
client = Client(account_sid, auth_token)

_rb = data.get("Conf", "rb")
_from = data.get("Conf", "from")
_to = data.get("Conf", "to")


# сравнение изображений
def compare(screen, template, thresh):
    screen = np.float32(screen)
    gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, np.float32(template), cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= thresh)
    total = np.count_nonzero(loc)
    return total, loc


# убить неизвестный процесс от игры
def kill_awe():
    awe = 'AwesomiumProcess.exe'
    for bill in psutil.process_iter():
        if bill.name() == awe:
            bill.kill()


# получить скриншот окна игры без фокуса по hwnd
def get_screenshot(hwnd):
    global SCREENSHOT
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    save_bit_map = win32ui.CreateBitmap()
    save_bit_map.CreateCompatibleBitmap(mfc_dc, w, h)
    save_dc.SelectObject(save_bit_map)
    windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 0)
    bmp_info = save_bit_map.GetInfo()
    bmp_str = save_bit_map.GetBitmapBits(True)
    SCREENSHOT = Image.frombuffer('RGB', (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_str, 'raw', 'BGRX', 0, 1)
    win32gui.DeleteObject(save_bit_map.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)
    return SCREENSHOT


# получить hwnd окон игры
def get_hwnd():
    for proc in psutil.process_iter():
        if proc.name() == process:
            def callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == proc.pid:
                        if hwnd not in windows:
                            windows.append(hwnd)
                return True

            win32gui.EnumWindows(callback, windows)


# проверка таргета на существование
def get_targeted_hp():
    template = cv2.imread('img/target_bar_close.png', 0)
    template_open = cv2.imread('img/target_bar_open.png', 0)
    res1, loc1 = compare(SCREENSHOT, template, 0.9)
    res2, loc2 = compare(SCREENSHOT, template_open, 0.9)
    if res1 == 2 or res2 == 2:
        return True
    else:
        return False


# получить имена персонажей в окнах
def get_name(hwnd):
    sfc = {}
    screen = np.array(get_screenshot(hwnd))
    gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('img/self_bar.png', 0)
    res1, loc1 = compare(screen, template, 0.9)
    if res1 == 2:
        for pt in zip(*loc1[::-1]):
            sfc = {"x": pt[0], "y": pt[1]}
    if not sfc:
        return -1
    cropped = gray[sfc["y"] + 8:sfc["y"] + 20, sfc["x"] + 42:sfc["x"] + 107]
    ret, bw = cv2.threshold(cropped, 148, 255, cv2.THRESH_BINARY_INV)
    connectivity = 4
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity, cv2.CV_32S)
    sizes = stats[1:, -1]
    nb_components = nb_components - 1
    min_size = 10
    img = np.zeros(output.shape, np.uint8)
    for i in range(0, nb_components):
        if sizes[i] >= min_size:
            img[output == i + 1] = 255
    res2 = cv2.bitwise_not(img)
    image_em = cv2.bitwise_not(res2)
    im = Image.fromarray(image_em)
    filename = ("%s.png" % os.getpid())
    im.save(filename)
    return filename


def send_message():
    for i in range(5):
        message = client.messages.create(
            body=_rb + ' реснулся!',
            from_='whatsapp:' + _from,
            to='whatsapp:' + _to
        )
        time.sleep(1)


# главный цикл
def mainloop(hwnd):
    kill_awe()
    while design.stay:
        try:
            autoit.win_activate_by_handle(hwnd)
            time.sleep(0.1)
            autoit.send("{NUMPAD0}")
            time.sleep(0.1)
            get_screenshot(hwnd)
            time.sleep(0.1)
            result = get_targeted_hp()
            if result:
                print("RaidBoss найден, отправляю оповещение")
                send_message()
                break
            else:
                print("RaidBoss не найден")
                time.sleep(10)
        except Exception:
            continue
