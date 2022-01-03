import os
import sys
import preview
from dataEmbedder import DataExtractor
from gui import downloader
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
from PyQt5 import QtWidgets


class extract_thread(QObject):
    def __init__(self):
        super(extract_thread, self).__init__()

    def do_extract(self):
        pass


class decrypt_thread(QObject):
    def __init__(self):
        super(decrypt_thread, self).__init__()

    def do_decrypt(self):
        pass


class downloader_main(QtWidgets.QDialog, downloader.Ui_Form, QThread):
    def __init__(self):
        super(downloader_main, self).__init__()
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.setupUi(self)
        self.setWindowTitle("Downloader")

        self.data_extractor = DataExtractor()

        self.child_window = None
        self.embed_data = None

        self.path_load_embed_key = None
        self.path_load_decrypt_key = None
        self.path_load_pic = None
        self.path_save_embed_data = None
        self.path_save_pic = None

        self.decrypt_qthread = QThread()
        self.extract_qthread = QThread()

        self.extract_thread = extract_thread()
        self.decrypt_thread = decrypt_thread()

        self.extract_thread.moveToThread(self.extract_qthread)
        self.decrypt_thread.moveToThread(self.decrypt_qthread)

        self.pushButton_explore_load_decrypt_key.clicked.connect(self.explore_load_decrypt_key)
        self.pushButton_explore_load_embed_key.clicked.connect(self.explore_load_embed_key)
        self.pushButton_explore_load_pic.clicked.connect(self.explore_load_pic)
        self.pushButton_preview_embed_data.clicked.connect(self.preview_embed_data)
        self.pushButton_save_embed_data.clicked.connect(self.save_embed_data)
        self.pushButton_decrypt_save_pic.clicked.connect(self.decrypt_save_pic)

    # 设定加载解密密钥路径
    def explore_load_decrypt_key(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,
                                        "Key Files (*.key);;")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_decrypt_key.setText(file_name)
            return

    # 设定加载嵌入密钥路径
    def explore_load_embed_key(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.txt);;All Files (*)")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_embed_key.setText(file_name)
            return

    # 设定加载图片路径
    def explore_load_pic(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.jpg);;")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_pic.setText(file_name)
            return

    # 预览嵌入信息
    def preview_embed_data(self):
        if self.embed_data != '':
            self.child_window = Child()
            self.child_window.show()
            self.child_window.preview(self.embed_data)
        else:
            QMessageBox.critical(None, "错误", "没有获得嵌入信息！", QMessageBox.Yes | QMessageBox.No)

        return

    def save_embed_data(self):
        file_name, filetype = \
            QFileDialog.getSaveFileName(None,
                                        "文件保存",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.txt);;All Files (*)")
        if file_name == "":  # 空路径
            QMessageBox.critical(None, "错误", "没有获得嵌入信息！", QMessageBox.Yes | QMessageBox.No)
            return
        else:
            f = open(file_name, 'w')
            f.write(self.embed_data)
            f.close()
            return

    def decrypt_save_pic(self):
        # TODO 解密产生原图片
        # 选择保存路径
        file_name, filetype = \
            QFileDialog.getSaveFileName(None,
                                        "文件保存",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.jpg);;")
        if file_name == "":  # 空路径
            return
        else:
            # TODO 保存解密图片文件
            return


class Child(QWidget):
    def __init__(self):
        super(Child, self).__init__()
        pre_ui = preview.Ui_Form()
        pre_ui.setupUi(self)
        self.setWindowTitle("嵌入信息预览")

    def preview(self, embed_data):
        self.textBrowser.setText(embed_data)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = downloader_main()
    main.show()
    sys.exit(app.exec_())
