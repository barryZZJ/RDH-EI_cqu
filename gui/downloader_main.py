import os
import sys
import preview
from gui import downloader
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget
from PyQt5 import QtWidgets


class downloader_main(QtWidgets.QDialog, downloader.Ui_Form, QThread):
    def __init__(self):
        super(downloader_main, self).__init__()
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.encode_pic = None
        self.decrypt_key = None
        self.embed_key = None
        self.embed_text = str('')
        self.setupUi(self)

        self.child_window = None

        self.setWindowTitle("Downloader")
        self.pushButton_explore_load_decrypt_key.clicked.connect(self.explore_load_decrypt_key)
        self.pushButton_explore_load_embed_key.clicked.connect(self.explore_load_embed_key)
        self.pushButton_explore_load_pic.clicked.connect(self.explore_load_pic)
        self.pushButton_preview_embed_text.clicked.connect(self.preview_embed_text)
        self.pushButton_save_embed_text.clicked.connect(self.save_embed_text)
        self.pushButton_decrypt_save_pic.clicked.connect(self.decrypt_save_pic)

    def explore_load_decrypt_key(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.txt);;All Files (*)")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_decrypt_key.setText(file_name)
            return

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

    def preview_embed_text(self):
        if self.embed_text != '':
            self.child_window = Child()
            self.child_window.show()
            self.child_window.preview(self.embed_text)
        else:
            QMessageBox.critical(None, "错误", "没有获得嵌入信息！", QMessageBox.Yes | QMessageBox.No)

        return

    def save_embed_text(self):
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
            f.write(self.embed_text)
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

    def preview(self, embed_text):
        self.textBrowser.setText(embed_text)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = downloader_main()
    main.show()
    sys.exit(app.exec_())
