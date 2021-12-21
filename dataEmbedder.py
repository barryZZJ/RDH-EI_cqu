from bitstring import BitStream
from typing import List
import json
from PIL import Image

from consts import *
from aesutil import AESUtil
from imgUil import segment_every

#! 测试数据使用consts.py中的常量，有改动在consts.py中修改
class DataEmbedder:
    """信息嵌入提取相关操作"""

    def __init__(self, config: str = EMBED_CONFIG_PATH, aesconfig: str = AES_CONFIG_PATH):
        """
        如果config不为空则从配置文件初始化self.key，
        否则随机初始化self.key。
        如果aesconfig不为空，初始化AESUtil，用于完美解密图片。
        *yzy*

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
        *yzy*

        :param config: 配置文件路径字符串
        """
        pass  # pass为占位符，实现时删掉该行

    def read_config(self, config: str = EMBED_CONFIG_PATH) -> str:
        """
        从配置文件中读取key，并返回key
        *yzy*

        :param config: 配置文件路径字符串
        """
        pass

    def rand_init(self) -> str:
        """
        随机初始化key，并返回key。TODO 密钥长度是否有影响。使用EMBED_KEY_LEN
        *yzy*
        """

        pass

    def embed(self, data: bytes, img: bytes) -> bytes:
        """
        把字节流data嵌入到密文字节流img中，返回嵌入后的字节流
        *zt*
        """
        pass

    def extract(self, img: bytes) -> bytes:
        """
        从字节流img中提取信息，返回提取出的信息字节流
        *yzy*
        """
        pass

    def perfect_decrypt(self):
        """
        如果同时拥有加密密钥和嵌入密钥，可以无损解密原始图片。
        需要调用AESUtil相关功能。
        我认为应该由信息嵌入器进行处理，因为该功能只有信息嵌入者知道。

        如果可以先提取再解密实现的话，就不需要这个函数

        *zzj*
        """
        if not self.aes: return
        pass

    def extract_LSB(self, img: BitStream) -> List[BitStream]:
        """
        提取出每块的LSB，组成列表。[c0^(0), c1^(0),...,ck-1^(0)]。共64bit * K

        *zt*
        """
        pass

    def shuffle(self, blocks_of_LSB: List[BitStream]) -> List[BitStream]:
        """
        打乱列表里的每个元素，要求算法可逆，密钥使用self.key。

        :param blocks_of_LSB: 以每块的LSB构成的列表

        *zt*
        """
        pass

    def reverse_shuffle(self, blocks_of_LSB: List[BitStream]) -> List[BitStream]:
        """
        上面算法的逆。

        :param blocks_of_LSB: 以每块的LSB构成的列表

        *zt*
        """
        pass

    def gen_matrix(self):
        """
        生成H=[I, Q]，其中Q用self.key随机初始化，返回矩阵H。
        *zt*
        """
        #注：矩阵操作可能要用到numpy库
        pass

    def encrypt_data(self, data: bytes) -> bytes:
        """
        对要嵌入的数据用self.key加密。
        *yzy*
        """
        # 可以用Crypto库里的现有算法。
        pass

    def sub_LSB(self, img: BitStream, sub: BitStream) -> BitStream:
        """
        把img中每一块的LSB替换为sub。根据实际情况sub可以改为List[BitStream]。
        *zt*
        """
        pass

    def sub_group_LSB(self, imgk: BitStream, sub: BitStream) -> BitStream:
        """
        把img中的一组的每一块的LSB替换为sub。考虑sub_LSB能否直接实现。
        *zzj*
        """
        pass

    def optimize(self, blocksk: List[List[Image.Image]]) -> int:
        """
        优化算法算出最合理的图片对应的情况。返回对应情况的下标。
        *zzj*
        """
        pass





