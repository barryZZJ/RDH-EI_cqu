import os
import sys
from gui import uploader
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets


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

    def explore_save_key(self):
        # TODO 默认文件名
        file_name, filetype = \
            QFileDialog.getSaveFileName(None,
                                        "文件保存",
                                        self.cwd,  # 起始路径
                                        "Text Files (*.key);;")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_save_key.setText(file_name)
            return

    def save_key(self):
        save_path = self.lineEdit_save_key.text()
        if save_path == '':
            self.label_save_flag.setText("<font color='red'>路径错误</font>")
            return
        f = open(save_path, 'w')
        if self.key != '':
            f.write(self.key)
            self.label_save_flag.setText("<font color='green'>保存成功</font>")
        else:
            self.label_save_flag.setText("<font color='red'>保存失败</font>")
        f.close()
        return

    def explore_load_key(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,  # 起始路径
                                        "Key Files (*.key);;")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_key.setText(file_name)
            return

    def explore_load_pic(self):
        file_name, filetype = \
            QFileDialog.getOpenFileName(None,
                                        "选取文件",
                                        self.cwd,  # 起始路径
                                        "Pic Files (*.jpg);;All Files (*)")
        if file_name == "":  # 空路径
            return
        else:
            # 将选中路径同步到LineEdit上
            self.lineEdit_load_pic.setText(file_name)
            return

    def save_encrypt_pic(self):
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
