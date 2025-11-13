import os
import random
import time
import pyautogui

#截取屏幕
#输入是截图保存地址
#输出是截图文件名
def fullscreen(path='./screenshot/', region=None):
    # 注意：在实际使用中，path参数应该从配置文件中获取，此处仅为默认值
    # 确保截图目录存在
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"创建截图目录: {path}")
    
    # 截取整个屏幕
    if region is None:
        screenshot = pyautogui.screenshot()
    else:
        # 截取指定区域 (x1, y1, width, height)
        # 例如，截取从左上角(0, 0)开始，宽度为300，高度为400的区域
        screenshot = pyautogui.screenshot(region=region)

    # 获取当前时间戳
    random_num = random.randint(0, 1000000)
    r = str(time.time()) + str(random_num)

    #filename - 使用os.path.join确保路径正确拼接
    filename = f'screenshot_{r}.png'
    name = os.path.join(path, filename)

    # 保存截图
    screenshot.save(name)
    print(f"截图已保存: {name}")

    return name

if __name__ == '__main__':
    name = fullscreen()
    print(name)
