import os  # 导入os模块，用于文件和目录操作
import cv2  # 导入OpenCV库，用于图像处理
from PyQt5.QtGui import QImage, QPixmap  # 导入PyQt5库中的图像和图标相关类
from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog,
    QSpinBox, QScrollArea, QGridLayout, QMainWindow, QDialog)
# 导入PyQt5库中的窗口部件类和布局类
from ImageSearchThread import ImageSearchThread


class ImageSearchWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图片搜索")  # 设置窗口标题
        self.setGeometry(100, 100, 800, 600)  # 设置窗口位置和大小
        self.create_widgets()  # 创建窗口部件
        self.similar_images_window = None  # 相似图像窗口
        self.selected_image = None  # 选择的图像
        self.thread = None  # 图像搜索线程

    def create_widgets(self):
        self.select_image_button = QPushButton("选择图片")  # 创建选择图片按钮
        self.select_image_button.clicked.connect(self.select_image)
        # 连接按钮的点击事件

        self.search_button = QPushButton("搜索")  # 创建搜索按钮
        self.search_button.clicked.connect(self.search_similar_images)
        # 连接按钮的点击事件

        self.num_images_label = QLabel("相似图片数量:")  # 创建相似图片数量标签
        self.num_images_spinbox = QSpinBox()  # 创建相似图片数量选择框
        self.num_images_spinbox.setMinimum(1)  # 设置最小值
        self.num_images_spinbox.setMaximum(50)  # 设置最大值
        self.num_images_spinbox.setValue(9)  # 设置默认值

        self.status_label = QLabel()  # 创建状态标签
        self.selected_image_label = QLabel()  # 创建显示选择的图片的标签

        layout = QVBoxLayout()  # 创建垂直布局
        layout.addWidget(self.select_image_button)  # 添加选择图片按钮到布局
        layout.addWidget(self.selected_image_label)  # 添加显示选择的图片的标签到布局
        layout.addWidget(self.search_button)  # 添加搜索按钮到布局
        layout.addWidget(self.num_images_label)  # 添加相似图片数量标签到布局
        layout.addWidget(self.num_images_spinbox)  # 添加相似图片数量选择框到布局
        layout.addWidget(self.status_label)  # 添加状态标签到布局

        self.setLayout(layout)  # 设置窗口的布局

    def select_image(self):
        file_dialog = QFileDialog()  # 创建文件选择对话框
        file_dialog.setNameFilter("Images (*.png *.xpm *.jpg *.bmp)")
        # 设置文件过滤器
        if file_dialog.exec_():  # 打开文件选择对话框
            selected_files = file_dialog.selectedFiles()  # 获取用户选择的文件路径
            self.selected_image_path = selected_files[0]  # 获取选择的第一个文件路径
            self.display_selected_image()  # 显示选择的图片
            self.status_label.setText(f"已选择图片: {self.selected_image_path}")
            # 将status_label的文本设置为显示所选图片的路径

    def display_selected_image(self):
        if hasattr(self, "selected_image_path"):
            # 检查selected_image_path属性是否存在
            self.selected_image = QImage(self.selected_image_path)

            # 从selected_image创建一个QPixmap对象
            pixmap = QPixmap.fromImage(self.selected_image)

            # # 将pixmap缩放到400x400像素的大小
            pixmap = pixmap.scaled(400, 400)

            # # 将pixmap设置为selected_image_label的内容
            self.selected_image_label.setPixmap(pixmap)

    def extract_feature(self, image):
        # 将图像转换为灰度图像
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 使用更高级的特征提取算法SIFT
        sift = cv2.SIFT_create()
        _, descriptors = sift.detectAndCompute(gray, None)  # 检测关键点和计算特征描述

        return descriptors  # 返回图像的特征描述

    def find_similar_images(self, target_feature, num_images):
        database_path = "D:/database"
        similar_images = []
        matcher = cv2.BFMatcher()
        # 遍历数据库文件夹
        for image_file in os.listdir(database_path):
            image_path = os.path.join(database_path, image_file)
            image = cv2.imread(image_path)

            # 提取图像特征
            image = cv2.resize(image, (400, 400))
            image_feature = self.extract_feature(image)

            # 使用更高级的特征匹配算法，例如FLANN
            matches = matcher.match(target_feature, image_feature)

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

    def search_similar_images(self):
        num_images = self.num_images_spinbox.value()  # 获取要搜索的相似图像数量

        if hasattr(self, "selected_image_path"):  # 检查是否存在选择的图像路径
            # 在搜索期间禁用搜索按钮
            self.search_button.setEnabled(False)

            # 显示正在搜索的消息
            self.status_label.setText("正在搜索中...")

            # 创建并启动图像搜索线程
            self.thread = ImageSearchThread(
                self.selected_image_path, num_images
            )

            # 连接搜索完成信号与显示相似图像的槽函数
            self.thread.search_finished.connect(self.display_similar_images)

            # 连接线程完成信号与搜索完成的槽函数
            self.thread.finished.connect(self.search_finished)

            self.thread.start()

        else:
            self.status_label.setText("请选择一张图片.")  # 如果没有选择图像，则显示提示消息

    def display_similar_images(self, similar_images):
        # 如果相似图像窗口已存在，则关闭窗口
        if self.similar_images_window:
            self.similar_images_window.close()

        # 创建相似图像窗口
        self.similar_images_window = QMainWindow()
        self.similar_images_window.setWindowTitle("相似图片")
        self.similar_images_window.setGeometry(200, 200, 800, 600)

        # 设置中央部件
        central_widget = QWidget()
        self.similar_images_window.setCentralWidget(central_widget)

        # 创建布局
        layout = QGridLayout(central_widget)

        # 在布局中添加相似图像
        for i, image_path in enumerate(similar_images):
            row = i // 3  # 计算行号
            col = i % 3  # 计算列号

            image_label = QLabel()
            image = QImage(image_path)
            pixmap = QPixmap.fromImage(image)
            pixmap = pixmap.scaled(200, 200)
            image_label.setPixmap(pixmap)

            # 点击图像时触发 show_image 方法，并传递对应的图像路径
            image_label.mousePressEvent = lambda event,\
                path=image_path: self.show_image(path)
            layout.addWidget(image_label, row, col)

        # 创建可滚动的区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(central_widget)

        # 设置相似图像窗口的中央部件为可滚动的区域
        self.similar_images_window.setCentralWidget(scroll_area)

        # 显示相似图像窗口
        self.similar_images_window.show()

    def search_finished(self):
        # 当搜索完成时，启用搜索按钮
        self.search_button.setEnabled(True)
        self.status_label.setText("搜索完成")

    def show_image(self, image_path):
        # 从给定路径读取图像
        image = QImage(image_path)
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(800, 600)

        # 创建一个对话框窗口用于显示图像
        image_dialog = QDialog(self)
        image_dialog.setWindowTitle("查看图片")
        image_dialog.setFixedSize(800, 600)

        # 创建布局
        layout = QVBoxLayout(image_dialog)

        # 在布局中添加图像标签
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        layout.addWidget(image_label)

        # 创建保存图片按钮，并连接到保存图片的方法
        save_button = QPushButton("保存图片")
        save_button.clicked.connect(lambda: self.save_image(image_path))
        layout.addWidget(save_button)

        # 执行对话框窗口
        image_dialog.exec_()

    def save_image(self, image_path):
        # 创建保存文件对话框
        save_dialog = QFileDialog()
        save_dialog.setAcceptMode(QFileDialog.AcceptSave)
        save_dialog.setDefaultSuffix("png")
        save_dialog.selectFile(image_path.split("/")[-1])

        # 如果保存对话框成功打开
        if save_dialog.exec_():
            # 获取选定的保存文件路径
            save_file_path = save_dialog.selectedFiles()[0]

            # 创建 QImage 对象
            image = QImage(image_path)

            # 将图像保存到指定路径
            if image.save(save_file_path):
                # 更新状态标签显示保存的文件路径
                self.status_label.setText(f"图片已保存: {save_file_path}")
            else:
                # 如果保存失败，显示保存失败的消息
                self.status_label.setText("保存图片失败")

    def save_similar_images(self, similar_images):
        # 选择保存文件夹
        save_dir = QFileDialog.getExistingDirectory(self, "选择保存路径")

        # 如果选择了保存文件夹
        if save_dir:
            # 遍历相似图像列表
            for image_path in similar_images:
                # 读取图像
                image = cv2.imread(image_path)

                # 获取图像名称
                image_name = os.path.basename(image_path)

                # 拼接保存路径
                save_path = os.path.join(save_dir, image_name)

                # 保存图像
                cv2.imwrite(save_path, image)

            # 更新状态标签显示保存成功的消息
            self.status_label.setText("图片保存成功！")
