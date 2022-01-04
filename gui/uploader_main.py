import os
import sys

from PyQt5.QtCore import *

from gui import uploader
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtWidgets
from aesutil import AESUtil
from imgUil import *
from bitstring import BitStream


class encrypt_thread(QObject):
    start_signal = pyqtSignal()
    finish_signal = pyqtSignal(str)

    def __init__(self, main_instance):
        super(encrypt_thread, self).__init__()
        self.main_instance = main_instance

    def do_encrypt(self):
        try:
            self.start_signal.emit()
            pic_bitstream = img_to_bitstream(self.main_instance.path_load_pic)
            # 加密
            pic_encrypted_bitstream = self.main_instance.aes_util.encrypt(pic_bitstream.bytes)
            # 加密结果转换为图片
            pic_encrypted = bitstream_to_img(BitStream(bytes=pic_encrypted_bitstream))
            pic_encrypted.save(self.main_instance.path_save_pic)
            self.finish_signal.emit('Y')
        except Exception as exc:
            QMessageBox.critical(None, "错误", str(exc), QMessageBox.Yes | QMessageBox.No)
            self.finish_signal.emit('N')


class uploader_main(QtWidgets.QDialog, uploader.Ui_Form, QThread):
    def __init__(self):
        super(uploader_main, self).__init__()

        self.path_load_pic = None
        self.path_load_key = None
        self.path_save_pic = None
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.setupUi(self)

        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Uploader")
        self.pushButton_explore_save_key.clicked.connect(self.explore_save_key)
        self.pushButton_save_key.clicked.connect(self.save_key)
        self.pushButton_explore_load_key.clicked.connect(self.explore_load_key)
        self.pushButton_explore_load_pic.clicked.connect(self.explore_load_pic)
        self.pushButton_save_encrypt_pic.clicked.connect(self.save_encrypt_pic)

        self.aes_util = AESUtil()
        self.encrypt_thread = encrypt_thread(self)
        self.thread = QThread()
        self.encrypt_thread.moveToThread(self.thread)
        self.thread.started.connect(self.encrypt_thread.do_encrypt)
        self.thread.finished.connect(self.thread_quit)
        self.encrypt_thread.start_signal.connect(self.encrypt_start)
        self.encrypt_thread.finish_signal.connect(self.encrypt_finish)

    # 浏览设定保存密钥路径
    def explore_save_key(self):
        # 保存文件浏览框
        file_name, filetype = \
            QFileDialog.getSaveFileName(self,
                                        "文件保存",
                                        self.cwd + "/aesConf",
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
        return

    # 设定加载密钥文件的路径
    def explore_load_key(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,
                                        "Key Files (*.key);;")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_key.setText(file_name)
            self.path_load_key = self.lineEdit_load_key.text()
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
            self.path_save_pic = self.lineEdit_load_pic.text()
            return

    # 加密并保存图片
    # noinspection PyBroadException
    def save_encrypt_pic(self):
        try:
            # 保存加密图片的路径
            file_name, filetype = \
                QFileDialog.getSaveFileName(self,
                                            "文件保存",
                                            self.cwd + "/untitled_encrypt",
                                            "BMP Pic Files (*.bmp);;"
                                            "JPG Pic Files (*.jpg);;"
                                            "PNG Pic Files (*.png);;"
                                            "All Files (*)")
            self.path_save_pic = file_name
            self.path_load_key = self.lineEdit_load_key.text()
            if self.path_load_key != '':
                print(self.path_load_key)
                self.aes_util.load_config(config=self.path_load_key)
            self.path_load_pic = self.lineEdit_load_pic.text()
            self.thread.start()

            return
        except IOError:
            QMessageBox.critical(None, "错误", "路径错误", QMessageBox.Yes | QMessageBox.No)
            self.label_encrypt_flag.setText("<font color='red'>保存失败</font>")
            return
        except Exception as e:
            QMessageBox.critical(None, "错误", str(e), QMessageBox.Yes | QMessageBox.No)
            self.label_encrypt_flag.setText("<font color='red'>保存失败</font>")
            return
        finally:
            return

    def encrypt_start(self):
        self.label_encrypt_flag.setText("<font color='red'>正在加密...</font>")
        return

    def encrypt_finish(self, info):
        if info == 'Y':
            self.label_encrypt_flag.setText("<font color='green'>保存成功</font>")
        else:
            self.label_encrypt_flag.setText("<font color='red'>保存失败</font>")
        self.thread_quit()
        return

    def thread_quit(self):
        self.thread.quit()

    def closeEvent(self, event):
        event.accept()
        os._exit(0)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = uploader_main()
    main.show()
    sys.exit(app.exec_())
