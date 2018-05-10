#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import math
import numpy
import random
import time

from PIL import Image
from match_img import match_img
from find_board import find_piece_and_board


# 获取屏幕截图
def get_screen_shot():
    source_file = "Content/WeChatJump.png"
    bak_file = "Content/WeChatJumpBak.png"
    os.system('adb shell screencap -p /sdcard/WeChatJump.png')
    if os.path.exists("Content/WeChatJump.png"):
        open(bak_file, "wb").write(open(source_file, "rb").read())
    os.system('adb pull /sdcard/WeChatJump.png Content')
    return source_file


# 备份截图
def bak_screen_shot(code):
    bak_file = "Log/Warning" + (time.strftime('%y%m%d%H%M%S', time.localtime(time.time()))) + ".png"
    source_file = "Content/WeChatJump.png"
    open(bak_file, "wb").write(open(source_file, "rb").read())
    if code == "Error":
        bak_file = "Log/Error" + (time.strftime('%y%m%d%H%M%S', time.localtime(time.time()))) + ".png"
        source_file = "Content/WeChatJumpBak.png"
        open(bak_file, "wb").write(open(source_file, "rb").read())


# 模拟按压键盘
def simulate_long_press(duration):
    os.system('adb shell input swipe 250 250 250 250 %s' % duration)


# 通过距离来计算按压持续时间
def calc_press_duration(distance):
    duration = distance * 1.35
    return duration


# 获取当前坐标
def get_current_coordinate(photo):
    # Way 1
    img_src = 'Content/Mark.png'
    img_match_result = match_img(img_src, photo, 0.5)
    if img_match_result is None:
        return [-1, -1]
    else:
        confidence = img_match_result["confidence"]
        if confidence < 0.7:
            return [-1, -1]
        else:
            result = img_match_result["result"]
            # 去除默认460px 去除边框40px
            x = result[0] - 460 - 40
            # 去除默认460px 去除边框40px
            y = result[1] - 750 - 20
            return [x, y]


# 获取当前坐标（方法2）
def get_current_coordinate2(photo):
    # Way 2
    im = Image.open(photo)
    im_pixel = im.load()
    # bg_color = im_pixel[100, 100]
    w, h = im.size
    piece_x = 0
    piece_x_count = 0
    piece_x_sum = 0
    piece_y = 0
    # piece_y_count = 0
    # piece_y_sum = 0
    scan_start_y = 0  # 扫描的起始y坐标

    for i in range(int(h / 3), int(h * 2 / 3), 50):
        last_pixel = im_pixel[0, i]
        for j in range(1, w):
            pixel = im_pixel[j, i]
            if pixel != last_pixel:
                scan_start_y = i - 50
                break
            if scan_start_y:
                break

    for i in range(scan_start_y, int(h * 2 / 3)):
        for j in range(int(w / 8), (w - int(w / 8))):
            pixel = im_pixel[j, i]
            if (50 < pixel[0] < 60) and (53 < pixel[1] < 63) and (95 < pixel[2] < 110):
                piece_x_sum += j
                piece_x_count += 1
                piece_y = max(i, piece_y)
    if piece_x_sum:
        piece_x = piece_x_sum / piece_x_count
    x = piece_x
    y = piece_y - 20
    return [x, y]


# 获取目标点坐标
def get_target_coordinate(current_coordinate, photo):
    # Way1
    mark_coo = current_coordinate
    mark_coo_x = mark_coo[0]
    mark_coo_y = mark_coo[1]

    im = Image.open(photo)
    im_pixel = im.load()
    w, h = im.size
    screen_center_coo = [int(w / 2), int(h / 2)]

    scan_start_x = 0
    scan_end_x = int(mark_coo_x)
    range_step_x = 1
    scan_start_y = int(h / 3)
    scan_end_y = int(mark_coo_y)
    range_step_y = 1

    board_coo_x = 0
    board_coo_y = 0

    if mark_coo_x < screen_center_coo[0]:
        scan_start_x = w - 1
        range_step_x = -range_step_x

    # 获取最高点或线的中间点位置坐标（获取x坐标）
    for j in range(scan_start_y, scan_end_y, range_step_y):
        start_pixel = im_pixel[scan_start_x, j]
        if board_coo_x or board_coo_y:
            # 重新设置x坐标扫描的结束位置
            scan_end_x = int(board_coo_x)
            # 重新设置y坐标扫描的开始位置
            scan_start_y = board_coo_y + 5
            # 重新设置y坐标扫描的结束位置
            scan_end_y = board_coo_y + 350
            break
        board_sum_x = 0
        board_count_x = 0
        for i in range(scan_start_x, scan_end_x, range_step_x):
            pixel = im_pixel[i, j]
            # 避免棋子过高
            if abs(i - mark_coo_x) < 40:
                continue
            diff = abs(pixel[0] - start_pixel[0]) + abs(pixel[1] - start_pixel[1]) + abs(pixel[2] - start_pixel[2])
            # print(diff)
            if diff > 10:
                board_sum_x += i
                board_count_x += 1
                board_coo_y = j
        if board_sum_x:
            board_coo_x = board_sum_x / board_count_x
    # print(int(board_coo_x), board_coo_y)

    # 通过获取到的最高点的中间位置获取到最右侧或最左侧点的位置（获取y坐标）
    pixels = []
    previous_x = w
    # previous_pixel = [-1, -1, -1]
    # print(previous_pixel)
    if range_step_x < 0:
        previous_x = 0
    # print('SCAN_Y:', scan_start_y, scan_end_y, range_step_y, '\nSCAN_X:', scan_start_x, scan_end_x, range_step_x, )
    for k in range(scan_start_y, scan_end_y, range_step_y):
        start_pixel = im_pixel[scan_start_x, k]
        for i in range(scan_start_x, scan_end_x, range_step_x):
            pixel = im_pixel[i, k]

            diff = abs(pixel[0] - start_pixel[0]) + abs(pixel[1] - start_pixel[1]) + abs(pixel[2] - start_pixel[2])
            if diff > 10:
                # 获取到边缘线的坐标集
                pixels.append([i, k])
                break

        # print(previous_x, i)
        # 往右侧跳动
        if range_step_x < 0 and previous_x >= i:
            break
        # 往左侧跳动
        if range_step_x > 0 and previous_x <= i:
            break
        # 上一次扫描的边框对应的x像素点
        previous_x = i

    # print(pixels)
    # 解析像素集，获取y坐标
    min_x = w
    max_x = 0
    for m in pixels:
        if range_step_x < 0:
            if max_x < m[0]:
                max_x = m[0]
                board_coo_y = m[1]
        if range_step_x > 0:
            if min_x > m[0]:
                min_x = m[0]
                board_coo_y = m[1]
    return [int(board_coo_x), board_coo_y]


# 获取目标点坐标（方法2）
def get_target_coordinate2(current_coordinate, photo):
    # Way 2
    im = Image.open(photo)
    im_pixel = im.load()
    w, h = im.size
    board_x = 0

    board_y = 0

    piece_x = current_coordinate[0]
    piece_y = current_coordinate[1]

    if piece_x < w / 2:
        board_x_start = piece_x
        board_x_end = w
    else:
        board_x_start = 0
        board_x_end = piece_x

    # print(['Test', piece_x, piece_y, int(board_x_start), int(board_x_end), int(h/3), piece_y])

    # 纵向检索，找到目标平台最上方的位置对应的x坐标
    for j in range(int(h / 3), int(piece_y)):
        last_pixel = im_pixel[board_x, j]
        if board_x or board_y:
            break
        board_x_count = 0
        board_x_sum = 0
        for i in range(int(board_x_start), int(board_x_end), 1):
            pixel = im_pixel[i, j]

            # 棋子过高
            if abs(i - piece_x) < 70:
                continue

            pix_diff = abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2])
            # print([i, j, pixDiff])
            if pix_diff > 10:
                board_x_sum += i
                board_x_count += 1
                if board_x_sum:
                    board_x = board_x_sum / board_x_count
                break

    # 横向检索，找到目标平台中间位置对应的y坐标
    for k in range(j + 275, j, -1):
        pixel = im_pixel[board_x, k]
        # 棋子过高
        if abs(i - piece_x) < 70:
            continue
        if abs(pixel[0] - last_pixel[0]) + abs(pixel[1] - last_pixel[1]) + abs(pixel[2] - last_pixel[2]) < 10:
            break
    board_y = int((j + k) / 2)

    for z in range(j, j + 200):
        pixel = im_pixel[board_x, i]
        if abs(pixel[0] - 245) + abs(pixel[1] - 245) + abs(pixel[1] - 245) == 0:
            board_y = z + 10
            break
    x = board_x
    y = board_y
    return [x, y]


# 通过当前坐标和目标坐标获取距离
def get_distance(current_coordinate, target_coordinate):
    x = target_coordinate[0] - current_coordinate[0]
    y = target_coordinate[1] - current_coordinate[1]
    distance = math.sqrt(numpy.square(x) + numpy.square(y))
    return distance


# 目标步数
def run(step):
    i = 1
    error_time = 1
    while i <= step:
        time.sleep(0.1)
        photo = get_screen_shot()
        time.sleep(0.1)
        current_coordinate = get_current_coordinate(photo)
        if current_coordinate[0] < 0:
            error_time = error_time + 1
            print('Error!')
            bak_screen_shot('Error')
            # return
            os.system('adb shell input tap 545 1580')

            if error_time >= 1:
                return

        else:
            target_coordinate = get_target_coordinate(current_coordinate, photo)
            piece_and_board = find_piece_and_board(Image.open(photo))
            print(piece_and_board)

            distance = get_distance(current_coordinate, target_coordinate)
            press_duration = calc_press_duration(distance)
            simulate_long_press(int(press_duration))
        i = i + 1
        random_sleep = random.uniform(0.2, 0.6)
        print([current_coordinate, target_coordinate, distance, press_duration, random_sleep])

        time.sleep(random_sleep)


# 主程序
def main():
    step = 100
    run(step)


if __name__ == '__main__':
    main()
