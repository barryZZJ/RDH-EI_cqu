import os
import sys
from gui import server
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets


class server_main(QtWidgets.QDialog, server.Ui_Form):
    def __init__(self):
        super(server_main, self).__init__()
        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.key = str('')
        self.pic = None
        self.embed_text = None
        self.embed_pic = None
        self.setupUi(self)

        self.setWindowTitle("Server")
        self.pushButton_explore_save_conf.clicked.connect(self.explore_save_conf)
        self.pushButton_save_conf.clicked.connect(self.save_conf)
        self.pushButton_explore_load_conf.clicked.connect(self.explore_load_conf)
        self.pushButton_explore_load_embed_text.clicked.connect(self.explore_load_embed_text)
        self.pushButton_explore_load_pic.clicked.connect(self.explore_load_pic)
        self.pushButton_save_pic.clicked.connect(self.save_embed_pic)

    def explore_save_conf(self):
        file_name, filetype = \
            QFileDialog.getSaveFileName(None,
                                        "文件保存",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.txt);;All Files (*)")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_save_conf.setText(file_name)
            return

    def save_conf(self):
        save_path = self.lineEdit_save_conf.text()
        if save_path == '':
            self.label_save_conf_flag.setText("路径错误")
            return
        f = open(save_path, 'w')
        if self.key != '':
            f.write(self.key)
            self.label_save_conf_flag.setText("保存成功")
        else:
            self.label_save_conf_flag.setText("保存失败")
        f.close()
        return

    def explore_load_conf(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.txt);;All Files (*)")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_conf.setText(file_name)
            return

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

    def save_embed_pic(self):
        # TODO 进行嵌入操作，获取嵌入后图片

        # 选择保存路径
        file_name, filetype = \
            QFileDialog.getSaveFileName(None,
                                        "文件保存",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.jpg);;")
        if file_name == "":  # 空路径
            self.label_save_pic_flag.setText("嵌入失败")
            return
        else:
            # TODO 保存嵌入文件

            self.label_save_pic_flag.setText("嵌入成功")
            return


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = server_main()
    main.show()
    sys.exit(app.exec_())
