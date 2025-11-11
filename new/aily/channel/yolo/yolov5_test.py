import torch
import cv2
import numpy as np

def identify(images, classes):
    # 加载模型
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    model.conf = 0.2  # 置信度阈值（只保留>0.4的目标）
    model.classes = classes  # 只检测汽车（过滤其他类别）

    # 读取图片
    img = cv2.imread(images)

    # 推理
    results = model(img)

    # 对图片处理标记
    # 可视化标记（自动画框+显示"car"和置信度）
    marked_img = np.squeeze(results.render())  # 渲染检测结果

    # 显示结果
    cv2.imshow('有车标记', marked_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 提取检测结果
    detections = results.pandas().xyxy[0]  # 转换为DataFrame格式
    # print(detections)
    return len(detections)


if __name__ == '__main__':
     count = identify('./demo.jpg', [0])
     print(count)
