import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QProgressBar,QMainWindow,QWidget, QHBoxLayout,QVBoxLayout, QLabel, QPushButton, QFileDialog
from PySide6.QtGui import QDropEvent, QDragEnterEvent,QPixmap,QMovie
from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Signal

from index import handle_images

class DropFrame(QFrame):
    file_dropped = Signal(str)
    clicked = Signal(str)
    file_path = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为0，使标签占据整个控件

        self.label = QLabel("拖拽文件夹或图片到此处", self)
        self.label.setAlignment(Qt.AlignCenter)  # 设置标签文本居中对齐
        layout.addWidget(self.label)
        
        self.clicked.connect(self.openFileDialog)
        
    def mousePressEvent(self, event):
        self.clicked.emit(event)

    def openFileDialog(self,event):
        self.clicked.disconnect(self.openFileDialog)  # 断开连接，防止再次触发
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.exec()
        selected_files = file_dialog.selectedFiles()
        if selected_files:
            file_path = selected_files[0]
            self.file_path.emit(file_path)
            self.label.setText(file_path)
        else:
            self.label.setText("拖拽文件夹或图片到此处")
            self.file_path.emit("")
            
        self.clicked.connect(self.openFileDialog)  # 断开连接，防止再次触发

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            # self.file_dropped.emit(url.toLocalFile())
            self.label.setText(url.toLocalFile())


class ImagePreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        self.label = QLabel(self)
        layout.addWidget(self.label)

    def show_image(self, image_path):
        pixmap = QPixmap(image_path)
        # scaled_pixmap = pixmap.scaledToWidth(self., Qt.SmoothTransformation)
        scaled_pixmap = pixmap.scaled(Qt.AspectRatioMode.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(scaled_pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(900, 700)
        self.setWindowTitle("Image Processing App")
        self.setStyleSheet("background: linear-gradient(to right, #feac5e, #c779d0, #4bc0c8);")
        self.file_path = ""

        main_layout = QVBoxLayout()
        
        # 预览
        # self.preview = ImagePreviewWidget()
        # main_layout.addWidget(self.preview,alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 创建一个可拖拽区域
        drop_frame = DropFrame()
        drop_frame.setFixedSize(600, 400) 
        drop_frame.setStyleSheet("border: 1px solid white;border-radius:8px;")
        drop_frame.file_dropped.connect(self.handle_file_dropped)
        drop_frame.file_path.connect(self.handle_file_dropped)
        main_layout.addWidget(drop_frame,alignment=Qt.AlignmentFlag.AlignCenter)
        
         # 创建一个标签用于显示拖拽的文件路径
        # self.file_label = QLabel("请先选择文件或者文件夹")
        # main_layout.addWidget(self.file_label,alignment=Qt.AlignmentFlag.AlignCenter)
        

        # 创建一个按钮用于开始处理图片
        self.process_button = QPushButton("开始处理")
        self.process_button.clicked.connect(self.start_processing)
        self.process_button.setFixedSize(80 ,60)
        self.process_button.setStyleSheet("background-color:#008e59; border-radius:8px;")
        main_layout.addWidget(self.process_button,alignment=Qt.AlignmentFlag.AlignCenter)
        
        # # 创建一个 QLabel 实例
        # self.loading_label = QLabel()
        # self.loading_label.setAlignment(Qt.AlignCenter)

        # # 创建一个 QMovie 实例并加载加载动画文件
        # self.loading_movie = QMovie(os.path.join(os.path.dirname(__file__),"./resource/images/loading.gif"))
        # self.loading_label.setMovie(self.loading_movie)

        # 将 QLabel 显示在按钮上
        # self.process_button.setFlat(True)
        # self.process_button.setStyleSheet("background-color:#008e59; border-radius:8px;")
        # self.process_button.setLayout(QHBoxLayout())
        # self.process_button.layout().addWidget(self.loading_label,alignment=Qt.AlignmentFlag.AlignCenter)
        
        # self.loading_movie.start()

        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # 创建一个占位的小部件
        placeholder_widget = QWidget()
        placeholder_widget.setLayout(main_layout)
        self.setCentralWidget(placeholder_widget)
    
        

    def handle_file_dropped(self, file_path):
        # print('file path',file_path)
        # self.file_label.setText(file_path)
        # 暂时用不上
        # self.preview.show_image(file_path)
        self.file_path = file_path
        if self.file_path == "":
            self.process_button.setText("开始处理")
            self.process_button.repaint()
            QApplication.processEvents()
        

    def start_processing(self):
        if self.file_path == None or self.file_path == "":
            return
        
        
        self.process_button.setText("处理中")
        self.process_button.setStyleSheet("background-color:#949c97; border-radius:8px;")
        self.process_button.repaint()
        QApplication.processEvents()
        # 在这里添加处理图片的逻辑
        handle_images(self.file_path)
        self.process_button.setText("处理完成✅")
        self.process_button.setStyleSheet("background-color:#008e59; border-radius:8px;")
        self.process_button.repaint()
        QApplication.processEvents()
        
       


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()