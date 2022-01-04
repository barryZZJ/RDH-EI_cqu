import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from dataEmbedder import DataEmbedder, DataLongError
from gui import server
from imgUil import img_to_bitstream, bitstream_to_img
from bitstring import BitStream


class encode_worker(QObject):
    encode_start_signal = pyqtSignal()
    encode_finish_signal = pyqtSignal(str)

    def __init__(self, main_instance):
        super(encode_worker, self).__init__()
        self.main_instance = main_instance
        self.data_bits = None
        self.img_bits = None

    def do_encode(self):
        try:
            self.encode_start_signal.emit()
            self.data_bits = self.main_instance.data_embedder.read_data(
                self.main_instance.path_load_data)
            self.img_bits = img_to_bitstream(self.main_instance.path_load_pic)
            self.encode_finish_signal.emit('Y')
        except Exception as e:
            QMessageBox.critical(None, "错误", str(e), QMessageBox.Yes | QMessageBox.No)
            self.encode_finish_signal.emit('N')

    def get_data(self):
        return [self.data_bits, self.img_bits]


class encrypt_worker(QObject):
    encrypt_start_signal = pyqtSignal()
    encrypt_finish_signal = pyqtSignal(str)

    def __init__(self, main_instance):
        super(encrypt_worker, self).__init__()
        self.main_instance = main_instance

    def do_embed(self):
        try:
            self.encrypt_start_signal.emit()
            # 嵌入
            embed_pic_bytes = self.main_instance.data_embedder.embed(
                data=self.main_instance.data_bits, img=self.main_instance.img_bits.bytes)
            # 保存图片
            embed_pic = bitstream_to_img(BitStream(bytes=embed_pic_bytes))
            embed_pic.save(self.main_instance.path_save_pic)
            self.encrypt_finish_signal.emit('Y')
        except IOError as e1:
            QMessageBox.critical(None, "错误", str(e1), QMessageBox.Yes | QMessageBox.No)
            self.encrypt_finish_signal.emit('N')
        except Exception as e2:
            QMessageBox.critical(None, "错误", str(e2), QMessageBox.Yes | QMessageBox.No)
            self.encrypt_finish_signal.emit('N')


class server_main(QtWidgets.QDialog, server.Ui_Form, QThread):
    def __init__(self):
        super(server_main, self).__init__()
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.setupUi(self)

        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Server")

        self.data_embedder = DataEmbedder()

        self.path_load_pic = None
        self.path_save_pic = None
        self.path_load_data = None
        self.path_load_conf = None

        self.data_bits = None
        self.img_bits = None

        # 线程定义
        self.encode_qthread = QThread()
        self.encrypt_qthread = QThread()
        self.encode_worker = encode_worker(self)
        self.encrypt_worker = encrypt_worker(self)
        self.encode_worker.moveToThread(self.encode_qthread)
        self.encrypt_worker.moveToThread(self.encrypt_qthread)

        # 启动线程
        self.encode_qthread.started.connect(self.encode_worker.do_encode)
        self.encrypt_qthread.started.connect(self.encrypt_worker.do_embed)
        self.encode_worker.encode_start_signal.connect(self.encode_thread_start)
        self.encrypt_worker.encrypt_start_signal.connect(self.encrypt_thread_start)

        # 结束线程
        self.encode_worker.encode_finish_signal.connect(self.encode_thread_finish)
        self.encrypt_worker.encrypt_finish_signal.connect(self.encrypt_thread_finish)
        self.encode_qthread.finished.connect(self.encode_thread_quit)
        self.encrypt_qthread.finished.connect(self.encrypt_thread_quit)

        # 控件信号
        self.pushButton_explore_save_conf.clicked.connect(self.explore_save_conf)
        self.pushButton_save_conf.clicked.connect(self.save_conf)
        self.pushButton_explore_load_conf.clicked.connect(self.explore_load_conf)
        self.pushButton_explore_load_data.clicked.connect(self.explore_load_data)
        self.pushButton_explore_load_pic.clicked.connect(self.explore_load_pic)
        self.pushButton_save_pic.clicked.connect(self.save_embed_pic)
        self.pushButton_calculate.clicked.connect(self.update_conf)

        self.lineEdit_load_pic.textChanged.connect(self.conf_change)
        self.lineEdit_load_data.textChanged.connect(self.conf_change)

        # 配置是否更新与文件匹配
        self.conf_newest_flag = False

        self.label_U.setText("U = " + str(self.data_embedder.PARAM_U))
        self.label_W.setText("W = " + str(self.data_embedder.PARAM_W))

    # 设定密钥和参数保存路径
    def explore_save_conf(self):
        file_name, filetype = \
            QFileDialog.getSaveFileName(None,
                                        "文件保存",
                                        self.cwd + "/embedConf",
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
            self.path_load_conf = self.lineEdit_load_conf.text()
            return

    # 设定加载嵌入文本的路径
    def explore_load_data(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.txt);;All Files (*)")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_data.setText(file_name)
            self.path_load_data = self.lineEdit_load_data.text()
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
            self.path_load_pic = self.lineEdit_load_pic.text()
            return

    # 保存嵌入后的图片
    def save_embed_pic(self):
        # 选择保存路径
        file_name, filetype = \
            QFileDialog.getSaveFileName(None,
                                        "文件保存",
                                        self.cwd + "/untitled_embed",
                                        "BMP Pic Files (*.bmp);;"
                                        "JPG Pic Files (*.jpg);;"
                                        "PNG Pic Files (*.png);;"
                                        "All Files (*)")
        if file_name == "":  # 空路径
            QMessageBox.critical(None, "错误", "路径错误", QMessageBox.Yes | QMessageBox.No)
            return
        # 加载各项路径
        self.path_save_pic = file_name
        self.path_load_data = self.lineEdit_load_data.text()
        self.path_load_conf = self.lineEdit_load_conf.text()
        if self.path_load_conf != '':
            self.data_embedder.load_config(config=self.path_load_conf)
        self.path_load_pic = self.lineEdit_load_pic.text()
        # 启动嵌入保存线程
        self.encrypt_qthread.start()
        return

    # 提示需要更新参数
    def conf_change(self):
        self.groupBox_conf.setTitle("当前参数（需要更新）")
        self.conf_newest_flag = False

    # 更新参数显示
    def update_conf(self):
        self.path_load_pic = self.lineEdit_load_pic.text()
        self.path_load_data = self.lineEdit_load_data.text()
        if self.path_load_pic == '':
            QMessageBox.critical(None, "错误", "无法加载目标图片", QMessageBox.Yes | QMessageBox.No)
        elif self.path_load_data == '':
            QMessageBox.critical(None, "错误", "无法加载嵌入文本", QMessageBox.Yes | QMessageBox.No)
        else:
            # 图片和文本都设定完成，开始编码并更新参数
            self.encode_qthread.start()
        return

    # 线程开始
    def encode_thread_start(self):
        self.pushButton_calculate.setText("正在计算...")
        self.pushButton_calculate.setEnabled(False)

    def encrypt_thread_start(self):
        self.pushButton_save_pic.setEnabled(False)
        self.label_save_pic_flag.setText("<font color='red'>正在嵌入...</font>")

    # 线程结束
    def encode_thread_finish(self, info):
        if info == 'Y':
            try:
                self.data_bits, self.img_bits = self.encode_worker.get_data()
                self.data_embedder.optimize_params(
                    data_bits=len(self.data_bits) * 8, img_bits=len(self.img_bits))
                self.label_U.setText('U = ' + str(self.data_embedder.PARAM_U))
                self.label_W.setText('W = ' + str(self.data_embedder.PARAM_W))
            except DataLongError as e1:
                QMessageBox.critical(None, "错误", str(e1), QMessageBox.Yes | QMessageBox.No)
            except ValueError as e2:
                QMessageBox.critical(None, "错误", str(e2), QMessageBox.Yes | QMessageBox.No)
            except Exception as e3:
                QMessageBox.critical(None, "错误", str(e3), QMessageBox.Yes | QMessageBox.No)
        else:
            QMessageBox.critical(None, "错误", "计算失败", QMessageBox.Yes | QMessageBox.No)
        self.encode_thread_quit()

    def encrypt_thread_finish(self, info):
        if info == 'Y':
            self.label_save_pic_flag.setText("<font color='green'>保存成功</font>")
        else:
            self.label_save_pic_flag.setText("<font color='red'>保存失败</font>")
        self.encrypt_thread_quit()

    # 线程退出
    def encode_thread_quit(self):
        self.pushButton_calculate.setText("自动计算参数")
        self.pushButton_calculate.setEnabled(True)
        self.groupBox_conf.setTitle("当前参数")
        self.conf_newest_flag = True
        self.encode_qthread.quit()
        return

    def encrypt_thread_quit(self):
        self.pushButton_save_pic.setEnabled(True)
        self.encrypt_qthread.quit()
        return

    def closeEvent(self, event):
        event.accept()
        os._exit(0)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = server_main()
    main.show()
    sys.exit(app.exec_())
