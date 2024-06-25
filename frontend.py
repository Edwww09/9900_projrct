import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, camera_index=1):
        super().__init__()
        self.camera_index = camera_index
        self._run_flag = True

    def run(self):
        # Capture video from the specified webcam
        cap = cv2.VideoCapture(self.camera_index)
        while self._run_flag:
            ret, frame = cap.read()
            if ret:
                # Flip the frame horizontally to correct the mirror effect
                frame = cv2.flip(frame, 1)
                # Convert the image to RGB
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert the image to QImage
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.change_pixmap_signal.emit(qt_image)
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()

class VideoWindow(QWidget):
    def __init__(self, camera_index=0):
        super().__init__()
        self.thread = VideoThread(camera_index)
        self.init_ui()

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle('Camera')
        self.setGeometry(100, 100, 800, 600)

        # 创建标签用于显示摄像头图像
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.resize(480, 480)

        # 创建垂直布局并添加标签
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)

        # 设置窗口的主布局
        self.setLayout(layout)

        # 连接线程的信号到更新图像的方法
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def update_image(self, qt_image):
        # 更新显示的摄像头图像
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        # 关闭窗口时终止线程
        self.thread.stop()
        event.accept()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle('PyQt5 Button')
        self.setGeometry(100, 100, 800, 600)

        # 创建按钮
        self.record_button = QPushButton('Record', self)
        self.upload_button = QPushButton('Upload', self)
        self.curve_button = QPushButton('Curve', self)
        self.close_button = QPushButton('Close', self)

        # 连接按钮点击事件到各自的槽函数
        self.record_button.clicked.connect(self.record_action)
        self.upload_button.clicked.connect(self.upload_action)
        self.curve_button.clicked.connect(self.curve_action)
        self.close_button.clicked.connect(self.close_action)

        # 创建垂直布局并添加按钮
        layout = QVBoxLayout()
        layout.addWidget(self.record_button)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.curve_button)
        layout.addWidget(self.close_button)

        # 设置窗口的主布局
        self.setLayout(layout)

    def record_action(self):
        # 打开新的摄像头窗口，使用索引 1 作为摄像头
        self.video_window = VideoWindow(camera_index=1)
        self.video_window.show()

    def upload_action(self):
        QMessageBox.information(self, 'Upload', 'Upload button clicked')

    def curve_action(self):
        QMessageBox.information(self, 'Curve', 'Curve button clicked')

    def close_action(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())
