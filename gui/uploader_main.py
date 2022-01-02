import os
import sys
import consts
from gui import uploader
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets
from aesutil import AESUtil


class uploader_main(QtWidgets.QDialog, uploader.Ui_Form):
    def __init__(self):
        super(uploader_main, self).__init__()
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.key = str('')
        self.pic = None
        self.encode_pic = None
        self.setupUi(self)

        self.setWindowTitle("Uploader")
        self.pushButton_explore_save_key.clicked.connect(self.explore_save_key)
        self.pushButton_save_key.clicked.connect(self.save_key)
        self.pushButton_explore_load_key.clicked.connect(self.explore_load_key)
        self.pushButton_explore_load_pic.clicked.connect(self.explore_load_pic)
        self.pushButton_save_encrypt_pic.clicked.connect(self.save_encrypt_pic)

        self.aes_util = AESUtil()

    # 浏览设定保存密钥路径
    def explore_save_key(self):
        # 保存文件浏览框
        file_name, filetype = \
            QFileDialog.getSaveFileName(self,
                                        "文件保存",
                                        self.cwd + consts.AES_CONFIG_PATH,  # 起始路径
                                        "Text Files (*.key);;")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_save_key.setText(file_name)
            return

    # 保存密钥，写入x.key文件
    def save_key(self):
        save_path = self.lineEdit_save_key.text()
        if save_path == '':
            self.label_save_flag.setText("<font color='red'>路径错误</font>")
            return
        try:
            # 保存key文件
            self.aes_util.save_config(config=save_path)
            self.label_save_flag.setText("<font color='green'>保存成功</font>")
        except IOError:
            self.label_save_flag.setText("<font color='red'>保存失败</font>")
            return

    # 设定加载密钥文件的路径
    def explore_load_key(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd + consts.AES_CONFIG_PATH,  # 起始路径
                                        "Key Files (*.key);;")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_key.setText(file_name)
            return

    # 设定加载原始图片的路径
    def explore_load_pic(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,  # 起始路径
                                        "BMP Pic Files (*.bmp);;"
                                        "JPG Pic Files (*.jpg);;"
                                        "PNG Pic Files (*.png);;"
                                        "All Files (*)")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_pic.setText(file_name)
            return

    # 加密并保存图片
    def save_encrypt_pic(self):
        # 检查是否使用加载密钥
        path_load_key = self.lineEdit_load_key.text()
        if path_load_key != '':
            self.aes_util.load_config(config=path_load_key)


        if self.encode_pic is not None:
            self.label_encryt_flag.setText("<font color='green'>保存成功</font>")
        else:
            self.label_encryt_flag.setText("<font color='red'>保存失败</font>")
        return


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = uploader_main()
    main.show()
    sys.exit(app.exec_())
