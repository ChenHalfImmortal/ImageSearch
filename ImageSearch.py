import sys  # 导入sys模块，用于处理命令行参数和退出应用程序
from PyQt5.QtGui import QIcon  # 导入PyQt5库中的图像和图标相关类
from PyQt5.QtWidgets import QApplication
# 导入PyQt5库中的窗口部件类和布局类
from ImageSearchWidget import ImageSearchWidget


if __name__ == "__main__":
    # 创建 QApplication 实例
    app = QApplication(sys.argv)

    # 创建 ImageSearchWidget 实例
    widget = ImageSearchWidget()

    # 显示 ImageSearchWidget
    widget.show()

    # 设置应用程序图标
    app_icon = QIcon("D:\\Picture\\icon1.ico")
    app.setWindowIcon(app_icon)

    # 运行应用程序的事件循环
    sys.exit(app.exec_())
