import json
from consts import *
from aesutil import AESUtil


class DataEmbedder:
    """信息嵌入提取相关操作"""

    def __init__(self, config: str = EMBED_CONFIG_PATH, aesconfig: str = AES_CONFIG_PATH):
        """
        如果config不为空则从配置文件初始化self.key，
        否则随机初始化self.key。
        如果aesconfig不为空，初始化AESUtil，用于完美解密图片。

        :param config: 配置文件路径字符串
        :param aesconfig: 加解密相关配置文件路径字符串
        """
        # 参考代码
        if config:
            self.key = self.read_config(config)
        else:
            self.key = self.rand_init()

        if aesconfig:
            self.aes = AESUtil(aesconfig)
        else:
            self.aes = None

    def save_config(self, config: str = EMBED_CONFIG_PATH):
        """
        保存key到配置文件中

        :param config: 配置文件路径字符串
        """
        pass  # pass为占位符，实现时删掉该行

    def read_config(self, config: str = EMBED_CONFIG_PATH) -> str:
        """
        从配置文件中读取key，并返回key

        :param config: 配置文件路径字符串
        """
        pass

    def rand_init(self) -> str:
        """随机初始化key，并返回key"""
        pass

    def embed(self, data: bytes, img: bytes) -> bytes:
        """把字节流data嵌入到密文字节流img中，返回嵌入后的字节流"""
        pass

    def extract(self, img: bytes) -> bytes:
        """从字节流img中提取信息，返回提取出的信息字节流"""
        pass

    def perfect_decrypt(self):
        """
        如果同时拥有加密密钥和嵌入密钥，可以无损解密原始图片。
        需要调用AESUtil相关功能。
        我认为应该由信息嵌入器进行处理，因为该功能只有信息嵌入者知道。
        """
        if not self.aes: return
        pass
