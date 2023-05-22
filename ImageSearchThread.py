import os  # 导入os模块，用于文件和目录操作
import cv2  # 导入OpenCV库，用于图像处理
# 导入PyQt5库中的窗口部件类和布局类
from PyQt5.QtCore import QThread, pyqtSignal  # 导入PyQt5库中的线程类和信号类


class ImageSearchThread(QThread):
    search_finished = pyqtSignal(list)  # 搜索完成信号，发送包含相似图像路径的列表

    def __init__(self, selected_image_path, num_images):
        super().__init__()
        self.selected_image_path = selected_image_path  # 被选择的图像路径
        self.num_images = num_images  # 需要搜索的相似图像数量

    def run(self):
        # 读取被选择的图像
        image = cv2.imread(self.selected_image_path)
        image = cv2.resize(image, (400, 400))  # 调整图像大小为固定尺寸

        # 提取被选择图像的特征
        target_feature = self.extract_feature(image)

        # 查找相似图像
        similar_images = self.find_similar_images(
            target_feature, self.num_images
        )

        # 发送包含相似图像路径的列表的信号
        self.search_finished.emit(similar_images)

        # 释放内存
        del image

    def extract_feature(self, image):
        # 将图像转换为灰度图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 使用更高级的特征提取算法SIFT
        sift = cv2.SIFT_create()
        _, descriptors = sift.detectAndCompute(gray, None)  # 检测关键点和计算特征描述

        return descriptors  # 返回图像的特征描述

    def find_similar_images(self, target_feature, num_images):
        database_path = "D:/database"  # 数据库文件夹路径
        similar_images = []  # 存储相似图像路径的列表
        matcher = cv2.BFMatcher()  # 使用暴力匹配算法

        # 遍历数据库文件夹
        for image_file in os.listdir(database_path):
            image_path = os.path.join(database_path, image_file)  # 构建图像文件的完整路径
            image = cv2.imread(image_path)  # 读取图像

            # 调整图像大小为固定尺寸
            image = cv2.resize(image, (400, 400))

            # 提取图像特征
            image_feature = self.extract_feature(image)

            # 使用更高级的特征匹配算法，例如FLANN
            matches = matcher.match(target_feature, image_feature)  # 匹配特征描述子

            # 计算匹配得分
            score = sum([match.distance for match in matches])

            # 添加相似图像和得分到列表中
            similar_images.append((score, image_path))

            # 释放内存
            del image

        # 根据得分对相似图像进行排序
        similar_images.sort(key=lambda x: x[0])

        # 选取前 num_images 张相似图像
        similar_images = [
            image_path for _, image_path in similar_images[:num_images]
        ]

        return similar_images  # 返回包含选取的相似图像路径的列表
