from bitstring import BitStream
from typing import List
import json
from PIL import Image

from consts import *
from aesutil import AESUtil
from imgUil import segment_every
from imgUil import img_to_bitstream
import  numpy as np

DEBUG = True
#! 测试数据使用consts.py中的常量，有改动在consts.py中修改
class DataEmbedder:
    """信息嵌入提取相关操作"""

    def __init__(self, config: str = None, aesconfig: str = None):
        """
        如果config不为空则从配置文件初始化self.key，
        否则随机初始化self.key。
        如果aesconfig不为空，初始化AESUtil，用于完美解密图片。
        *yzy*

        :param config: 配置文件路径字符串
        :param aesconfig: 加解密相关配置文件路径字符串

        # 参考代码
        if DEBUG:
            self.key = EMBED_KEY_DEBUG
        else:
            if config:
                self.key = self.read_config(config)
            else:
                self.key = self.rand_init()

        if aesconfig:
            self.aes = AESUtil(aesconfig)
        else:
            self.aes = None
        """


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
        # 每一个块是8*8*8=512bit，经过图片转换成字节流，每个块的前64bit就是每块的LSB
        lsbs = [] #全部块的LSB列表
        for k in range(0,int(len(img)/512)):
            lsbs.append(img[k*512:k*512+64])
        return lsbs

    def shuffle(self, blocks_of_LSB: List[BitStream]) -> List[BitStream]:
        """
        打乱列表里的每个元素，要求算法可逆，密钥使用self.key。

        :param blocks_of_LSB: 以每块的LSB构成的列表

        *zt*
        """
        #使用self.key作为种子设置random,然后生成一个K长度的随机数列
        np.random.seed(int.from_bytes(self.key,byteorder='big',signed=False)%(2**32-1))
        #测试用np.random.seed((int.from_bytes(EMBED_KEY_DEBUG, byteorder='big', signed=False))%(2**32-1))
        rlist=np.random.permutation(len(blocks_of_LSB))
        #然后按照随机数列给原数列打乱
        new_blocks_of_LSB=[]
        for i in range(0,len(blocks_of_LSB)):
            new_blocks_of_LSB.append(blocks_of_LSB[rlist[i]])
        return new_blocks_of_LSB




    def reverse_shuffle(self, blocks_of_LSB: List[BitStream]) -> List[BitStream]:
        """
        上面算法的逆。

        :param blocks_of_LSB: 以每块的LSB构成的列表

        *zt*
        """
        #使用self.key作为种子设置random,然后生成一个K长度的随机数列，再把这个数列的逆数列求出来
        np.random.seed(int.from_bytes(self.key,byteorder='big',signed=False)%(2**32-1))
        # 测试用np.random.seed((int.from_bytes(EMBED_KEY_DEBUG, byteorder='big', signed=False)) % (2 ** 32 - 1))
        rlist = np.random.permutation(len(blocks_of_LSB))
        rrlist=[0]*len(blocks_of_LSB)
        for i in range(0,len(blocks_of_LSB)):
            rrlist[rlist[i]]=i
        #然后按照逆随机数列把打乱数列还原
        new_blocks_of_LSB = []
        for i in range(0, len(blocks_of_LSB)):
            new_blocks_of_LSB.append(blocks_of_LSB[rrlist[i]])
        return new_blocks_of_LSB

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


if __name__ == '__main__':
    #测试用
    """
    img=img_to_bitstream(PIC_16_PATH)
    test=DataEmbedder()
    list=test.extract_LSB(img)
    print(list)
    list1=test.shuffle(list)
    print(list1)
    list2=test.reverse_shuffle(list1)
    print(list2)
    """


