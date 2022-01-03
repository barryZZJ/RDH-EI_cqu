import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from dataEmbedder import DataEmbedder
from gui import server
from imgUil import img_to_bitstream, bitstream_to_img
from bitstring import BitStream


class server_main(QtWidgets.QDialog, server.Ui_Form, QThread):
    def __init__(self):
        super(server_main, self).__init__()
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.setupUi(self)
        self.setWindowTitle("Server")

        self.path_load_pic = None
        self.path_save_pic = None
        self.path_load_data = None

        self.data_bits = None
        self.img_bits = None

        self.encode_thread = QThread()
        self.encrypt_thread = QThread()



        self.pushButton_explore_save_conf.clicked.connect(self.explore_save_conf)
        self.pushButton_save_conf.clicked.connect(self.save_conf)
        self.pushButton_explore_load_conf.clicked.connect(self.explore_load_conf)
        self.pushButton_explore_load_embed_text.clicked.connect(self.explore_load_embed_text)
        self.pushButton_explore_load_pic.clicked.connect(self.explore_load_pic)
        self.pushButton_save_pic.clicked.connect(self.save_embed_pic)
        self.pushButton.clicked.connect(self.update_conf)

        self.data_embedder = DataEmbedder()


    # 设定密钥和参数保存路径
    def explore_save_conf(self):
        file_name, filetype = \
            QFileDialog.getSaveFileName(None,
                                        "文件保存",
                                        self.cwd,
                                        "Text Files (*.key);;")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_save_conf.setText(file_name)
            return

    # 保存密钥和参数
    def save_conf(self):
        save_path = self.lineEdit_save_conf.text()
        if save_path == '':
            self.label_save_conf_flag.setText("路径错误")
            return
        try:
            # 保存配置文件
            self.data_embedder.save_config(config=save_path)
            self.label_save_conf_flag.setText("<font color='green'>保存成功</font>")
        except IOError:
            self.label_save_conf_flag.setText("<font color='red'>保存失败</font>")
            return
        return

    # 设定加载密钥和参数的路径
    def explore_load_conf(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,
                                        "Text Files (*.key);;")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_conf.setText(file_name)
            return

    # 设定加载嵌入文本的路径
    def explore_load_embed_text(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.txt);;All Files (*)")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_embed_text.setText(file_name)
            return

    # 设定加载图片的路径
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

    # 保存嵌入后的图片
    def save_embed_pic(self):
        try:
            # 选择保存路径
            file_name, filetype = \
                QFileDialog.getSaveFileName(None,
                                            "文件保存",
                                            self.cwd,
                                            "BMP Pic Files (*.bmp);;"
                                            "JPG Pic Files (*.jpg);;"
                                            "PNG Pic Files (*.png);;"
                                            "All Files (*)")
            if file_name == "":  # 空路径
                self.label_save_pic_flag.setText("嵌入失败")
                return
            # 加载各项路径
            self.path_save_pic = file_name
            self.path_load_data = self.lineEdit_load_data.text()
            if self.path_load_data != '':
                self.data_embedder.load_config(config=self.path_load_data)
            self.path_load_pic = self.lineEdit_load_pic.text()

            embed_pic_bitstream = self.data_embedder.embed(data=self.data_bits, img=self.img_bits.bytes)

            # 保存图片
            embed_pic = bitstream_to_img(BitStream(embed_pic_bitstream))
            embed_pic.save(self.path_save_pic)

            self.label_save_pic_flag.setText("<font color='green'>嵌入成功</font>")
            return
        except IOError as e1:
            QMessageBox.critical(None, "错误", str(e1), QMessageBox.Yes | QMessageBox.No)
            self.label_save_pic_flag.setText("<font color='red'>嵌入失败</font>")
            return
        except Exception as e2:
            QMessageBox.critical(None, "错误", str(e2), QMessageBox.Yes | QMessageBox.No)
            self.label_save_pic_flag.setText("<font color='red'>嵌入失败</font>")
            return
        finally:
            return

    # 更新参数显示
    def update_conf(self):
        if self.lineEdit_load_pic == '':
            QMessageBox.critical(None, "错误", "无法加载目标图片", QMessageBox.Yes | QMessageBox.No)
        elif self.lineEdit_load_embed_text == '':
            QMessageBox.critical(None, "错误", "无法加载嵌入文本", QMessageBox.Yes | QMessageBox.No)
        else:
            self.data_bits = self.data_embedder.read_data(self.path_load_data)
            self.img_bits = img_to_bitstream(self.path_load_pic)
            self.data_embedder.optimize_params(
                data_bits=len(self.data_bits)*8, img_bits=len(self.img_bits)*8)
        self.label_U.setText('U = ' + str(self.data_embedder.PARAM_U))
        self.label_W.setText('W = ' + str(self.data_embedder.PARAM_W))
        return


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = server_main()
    main.show()
    sys.exit(app.exec_())
