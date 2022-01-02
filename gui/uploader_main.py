import os
import sys

from PyQt5.QtCore import QThread

import consts
from gui import uploader
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtWidgets
from aesutil import AESUtil
from imgUil import *
from bitstring import BitStream


class encrypt_thread(QThread):
    def __init__(self, client):
        super(encrypt_thread, self).__init__()
        self.client = client

    def run(self):
        try:
            self.client.label_encrypt_flag.setText("<font color='yellow'>正在加密...</font>")
            pic_bitstream = img_to_bitstream(self.client.path_load_pic)
            # 加密
            pic_encrypted_bitstream = self.client.aes_util.encrypt(pic_bitstream.bytes)
            # 加密结果转换为图片
            pic_encrypted = bitstream_to_img(BitStream(bytes=pic_encrypted_bitstream))
            pic_encrypted.save(self.client.path_save_pic)
            self.client.label_encrypt_flag.setText("<font color='green'>保存成功</font>")
        except Exception as exc:
            QMessageBox.critical(None, "错误", str(exc), QMessageBox.Yes | QMessageBox.No)
            self.terminate()


class uploader_main(QtWidgets.QDialog, uploader.Ui_Form):
    def __init__(self):
        super(uploader_main, self).__init__()
        self.path_load_pic = None
        self.path_load_key = None
        self.path_save_pic = None
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.setupUi(self)

        self.setWindowTitle("Uploader")
        self.pushButton_explore_save_key.clicked.connect(self.explore_save_key)
        self.pushButton_save_key.clicked.connect(self.save_key)
        self.pushButton_explore_load_key.clicked.connect(self.explore_load_key)
        self.pushButton_explore_load_pic.clicked.connect(self.explore_load_pic)
        self.pushButton_save_encrypt_pic.clicked.connect(self.save_encrypt_pic)

        self.aes_util = AESUtil()
        self.encrypt_thread = None

    def set_thread(self, thread):
        self.encrypt_thread = thread

    # 浏览设定保存密钥路径
    def explore_save_key(self):
        # 保存文件浏览框
        file_name, filetype = \
            QFileDialog.getSaveFileName(self,
                                        "文件保存",
                                        self.cwd + "/" + consts.AES_CONFIG_PATH,
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
                                        self.cwd + "/" + consts.AES_CONFIG_PATH,
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
                                        self.cwd,
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
    # noinspection PyBroadException
    def save_encrypt_pic(self):
        try:
            # 保存加密图片的路径
            file_name, filetype = \
                QFileDialog.getSaveFileName(self,
                                            "文件保存",
                                            self.cwd + "/untitled.jpg",
                                            "BMP Pic Files (*.bmp);;"
                                            "JPG Pic Files (*.jpg);;"
                                            "PNG Pic Files (*.png);;"
                                            "All Files (*)")
            self.path_save_pic = file_name
            self.path_load_key = self.lineEdit_load_key.text()
            if self.path_load_key != '':
                self.aes_util.load_config(config=self.path_load_key)
            # 加载原始图片
            self.path_load_pic = self.lineEdit_load_pic.text()
            self.encrypt_thread.run()
            return
        except IOError:
            self.label_encrypt_flag.setText("<font color='red'>保存失败</font>")
            return
        except Exception as e:
            QMessageBox.critical(None, "错误", str(e), QMessageBox.Yes | QMessageBox.No)
            self.label_encrypt_flag.setText("<font color='red'>保存失败</font>")
            return
        finally:
            return


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = uploader_main()
    e_t = encrypt_thread(main)
    main.set_thread(e_t)
    main.show()
    sys.exit(app.exec_())
