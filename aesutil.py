from typing import Tuple
import json
from consts import *


class AESUtil:
    """加密解密相关操作"""

    def __init__(self, config: str = AES_CONFIG_PATH):
        """
        如果config不为空则从配置文件初始化self.iv和self.key，
        否则随机初始化self.iv和self.key。

        :param config: 配置文件路径字符串
        """
        # 参考代码
        if config:
            self.iv, self.key = self.read_config(config)
        else:
            self.iv, self.key = self.rand_init()

    def save_config(self, config: str = AES_CONFIG_PATH):
        """
        保存iv和key到配置文件中，可以考虑构建字典然后JSON.dump，则配置文件后缀名为.json

        :param config: 配置文件路径字符串
        """
        pass  # pass为占位符，实现时删掉该行

    def read_config(self, config: str = AES_CONFIG_PATH) -> Tuple[str, str]:
        """
        从配置文件中读取iv和key，可以考虑用JSON.load读取字典，并返回(iv, key)二元组

        :param config: 配置文件路径字符串
        """
        pass

    def rand_init(self) -> Tuple[str, str]:
        """随机初始化iv和key，并返回(iv, key)二元组"""
        pass

    def encrypt(self, m: bytes) -> bytes:
        """对明文字节流m加密，返回密文字节流"""
        pass

    def decrypt(self, c: bytes) -> bytes:
        """对密文字节流c解密，返回明文字节流"""
        pass
