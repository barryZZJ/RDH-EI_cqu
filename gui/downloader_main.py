import os
import sys
import preview
from aesutil import AESUtil
from dataEmbedder import DataExtractor
from imgUil import img_to_bitstream, bitstream_to_img
from gui import downloader
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtWidgets
from bitstring import BitStream


class extract_thread(QObject):
    extract_finish_signal = pyqtSignal()

    def __init__(self, main_instance):
        super(extract_thread, self).__init__()
        self.main_instance = main_instance

    def do_extract(self):
        try:
            pic_bitstream = img_to_bitstream(self.main_instance.path_load_pic)
            self.main_instance.img_bits = pic_bitstream
            self.main_instance.embed_data = self.main_instance.data_extractor.extract(img=pic_bitstream.bytes)
        except Exception as e:
            QMessageBox.critical(None, "错误", str(e), QMessageBox.Yes | QMessageBox.No)
        finally:
            self.extract_finish_signal.emit()


class decrypt_thread(QObject):
    decrypt_finish_signal = pyqtSignal()

    def __init__(self, main_instance):
        super(decrypt_thread, self).__init__()
        self.main_instance = main_instance

    def do_decrypt(self):
        try:
            perfect_bits = self.main_instance.data_extractor.perfect_decrypt(
                data=self.main_instance.embed_data, img=self.main_instance.img_bits)
            perfect_img = bitstream_to_img(BitStream(bytes=perfect_bits))
            perfect_img.save(self.main_instance.path_save_pic)
        except IOError:
            QMessageBox.critical(None, "错误", "路径错误", QMessageBox.Yes | QMessageBox.No)
        except Exception as e:
            QMessageBox.critical(None, "错误", str(e), QMessageBox.Yes | QMessageBox.No)
        finally:
            self.decrypt_finish_signal.emit()


class downloader_main(QtWidgets.QDialog, downloader.Ui_Form, QThread):
    def __init__(self):
        super(downloader_main, self).__init__()
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.setupUi(self)
        self.setWindowTitle("Downloader")

        self.data_extractor = DataExtractor()
        self.aes_util = AESUtil()

        self.child_window = None
        self.embed_data = bytes()
        self.img_bits = None

        # 路径
        self.path_load_embed_key = None
        self.path_load_decrypt_key = None
        self.path_load_pic = None
        self.path_save_embed_data = None
        self.path_save_pic = None

        # 线程定义
        self.decrypt_qthread = QThread()
        self.extract_qthread = QThread()
        self.extract_thread = extract_thread(self)
        self.decrypt_thread = decrypt_thread(self)
        self.extract_thread.moveToThread(self.extract_qthread)
        self.decrypt_thread.moveToThread(self.decrypt_qthread)

        # 启动线程
        self.extract_qthread.started.connect(self.extract_thread.do_extract)
        self.decrypt_qthread.started.connect(self.decrypt_thread.do_decrypt)

        # 结束线程
        self.extract_thread.extract_finish_signal.connect(self.extract_thread_quit)
        self.decrypt_thread.decrypt_finish_signal.connect(self.decrypt_thread_quit)
        self.extract_qthread.finished.connect(self.extract_thread_quit)
        self.decrypt_qthread.finished.connect(self.decrypt_thread_quit)

        # 控件信号
        self.pushButton_explore_load_decrypt_key.clicked.connect(self.explore_load_decrypt_key)
        self.pushButton_explore_load_embed_key.clicked.connect(self.explore_load_embed_key)
        self.pushButton_explore_load_pic.clicked.connect(self.explore_load_pic)
        self.pushButton_preview_embed_data.clicked.connect(self.preview_embed_data)
        self.pushButton_save_embed_data.clicked.connect(self.save_embed_data)
        self.pushButton_decrypt_save_pic.clicked.connect(self.decrypt_save_pic)

        # 是否可以进行完全解密
        self.perfect_flag = False

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
                                        self.cwd,
                                        "Key Files (*.key);;")
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
            self.embed_data = None
            return

    # 获取嵌入信息
    def get_embed_data(self):
        self.data_extractor.load_config(config=self.path_load_embed_key)
        self.extract_qthread.start()

    # 预览嵌入信息
    def preview_embed_data(self):
        self.get_embed_data()
        if self.embed_data is not None:
            self.child_window = Child()
            self.child_window.show()
            self.child_window.preview(str(self.embed_data))
        else:
            QMessageBox.critical(None, "错误", "没有获得嵌入信息！", QMessageBox.Yes | QMessageBox.No)
        return

    # 保存嵌入信息
    def save_embed_data(self):
        file_name, filetype = \
            QFileDialog.getSaveFileName(None,
                                        "文件保存",
                                        self.cwd + "/extracted_data",  # 起始路径
                                        "Text Files (*.txt);;All Files (*)")
        if file_name == "":  # 空路径
            QMessageBox.critical(None, "错误", "不存在的路径", QMessageBox.Yes | QMessageBox.No)
            return
        else:
            if self.embed_data is None:
                QMessageBox.critical(None, "错误", "无信息：尝试点击预览获取", QMessageBox.Yes | QMessageBox.No)
            self.path_save_embed_data = file_name
            self.data_extractor.save_data(data=self.embed_data, file_path=self.path_save_embed_data)
            return

    # 解密并保存图片
    def decrypt_save_pic(self):
        # 选择保存路径
        file_name, filetype = \
            QFileDialog.getSaveFileName(None,
                                        "文件保存",
                                        self.cwd + "/untitled_extract",  # 起始路径
                                        "BMP Pic Files (*.bmp);;"
                                        "JPG Pic Files (*.jpg);;"
                                        "PNG Pic Files (*.png);;"
                                        "All Files (*)")
        if file_name == "":  # 空路径
            return
        else:
            self.path_save_pic = file_name
            self.path_load_decrypt_key = self.lineEdit_load_decrypt_key.text()
            if self.path_load_decrypt_key is not None:
                self.aes_util.load_config(self.path_load_decrypt_key)
                self.data_extractor.load_config(aesutil=self.aes_util)
                if self.embed_data is not None:
                    self.perfect_flag = True
                else:
                    self.perfect_flag = False
            else:
                QMessageBox.critical(None, "错误", "无密钥", QMessageBox.Yes | QMessageBox.No)
            # 启动解密保存线程
            self.decrypt_qthread.start()
            return

    # 线程结束退出
    def extract_thread_quit(self):
        self.extract_qthread.quit()
        return

    def decrypt_thread_quit(self):
        QMessageBox.information(self, "提示", "保存成功", QMessageBox.Yes)
        self.decrypt_qthread.quit()
        return


class Child(QtWidgets.QDialog, preview.Ui_Form):
    def __init__(self):
        super(Child, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("嵌入信息预览")

    def preview(self, embed_data):
        self.textBrowser.setText(embed_data)
        self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = downloader_main()
    main.show()
    sys.exit(app.exec_())
