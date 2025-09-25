import time
import pyautogui

#截取屏幕
#输入是截图保存地址
#输出是截图文件名
def fullscreen(path, region=None):
    # 截取整个屏幕
    if region is None:
        screenshot = pyautogui.screenshot()
    else:
        # 截取指定区域 (x1, y1, width, height)
        # 例如，截取从左上角(0, 0)开始，宽度为300，高度为400的区域
        screenshot = pyautogui.screenshot(region=region)

    # 获取当前时间戳
    timestamp = int(time.time())

    #filename
    name = path + 'screenshot_{}.png'.format(timestamp)

    # 保存截图
    screenshot.save(name)

    return name

if __name__ == '__main__':
    name = fullscreen()

    print(name)
