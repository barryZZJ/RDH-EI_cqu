import numpy as np
from bitstring import BitStream
from typing import List
import json
from PIL import Image

from consts import *
from aesutil import AESUtil
from imgUil import segment_every, join, bitstream_to_blocks, _from_blocks
#TODO 添加可嵌入量接口
DEBUG = True
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

    def perfect_decrypt(self, data: bytes, img: bytes) -> Image.Image:
        """
        如果同时拥有加密密钥和嵌入密钥，可以无损解密原始图片。
        需要调用AESUtil相关功能。
        我认为应该由信息嵌入器进行处理，因为该功能只有信息嵌入者知道。

        *zzj*
        """
        assert isinstance(self.aes, AESUtil)
        img = BitStream(bytes=img)
        blocks_of_LSB = self.extract_LSB(img)
        blocks_of_LSB = self.reverse_shuffle(blocks_of_LSB)
        bitstream_LSB = join(blocks_of_LSB)
        K = len(blocks_of_LSB)
        L = K//EMBED_PARAM_U
        # 把bitstream_LSB分成L个组，每组包含了u个块的LSB，每组为64*u bit
        g = segment_every(bitstream_LSB, 64*EMBED_PARAM_U)
        H = self.gen_matrix()
        data = self.encrypt_data(data)
        data = BitStream(bytes=data)
        datas = segment_every(data, EMBED_PARAM_W)
        # 以组为单位，尝试恢复 gk
        # 恢复原理：遍历 gk[:w]所有可能的取值，全部解密出原图（共w位，故2^w个图），通过数字统计关系选出最合理的那一个
        best_blocks = []
        e_grouped = segment_every(img, 512*EMBED_PARAM_U)  # u个块(64b*8 * u)一组，共L组
        for k in range(0, L-1 + 1):
            blocks_k = [None] * (2**EMBED_PARAM_W)  # type: List[List[Image.Image]] # shape: (2^w, u)
            # blocks_k[l] = 第k组中，第l种情况的u个块
            e_k = e_grouped[k].copy()  # FIXME 能否删除copy
            for l in range(2**EMBED_PARAM_W):
                t_l = BitStream(uint=l, length=EMBED_PARAM_W)
                r_k = datas[k] ^ t_l
                w_k = g[k] ^ self.dot(r_k, H)  # TODO 点乘待实现
                e_k = self.sub_group_LSB(e_k, w_k)  # 把e_k的LSB替换为w_k，即论文中的r
                e_k = self.aes.decrypt(e_k.bytes, iv=e_grouped[k-1][-128:].bytes if k > 0 else None)  # TODO 正确性待检查 # 只解密第k组的u个块，iv为上一组的最后128bit
                e_k = BitStream(bytes=e_k)
                P_kl = bitstream_to_blocks(e_k)  # u个8x8的像素块列表
                blocks_k[l] = P_kl  # 记录第l种情况下的u个块
            best_l = self.optimize(blocks_k)  # TODO 正确性待检查
            best_blocks.extend(blocks_k[best_l])  # 最合理的u个块添加到结果中
        best_img = _from_blocks(best_blocks)
        return best_img

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

    #TODO
    def dot(self, bits: BitStream, matrix) -> BitStream:
        """
        比特流与矩阵点乘
        """
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

    # TODO
    def sub_group_LSB(self, imgk: BitStream, sub: BitStream) -> BitStream:
        """
        把img中的一组的每一块的LSB替换为sub。考虑sub_LSB能否直接实现。
        *zzj*
        """
        pass

    def optimize(self, blocks_k: List[List[Image.Image]]) -> int:
        """
        优化算法算出最合理的图片对应的情况。返回该情况对应的下标。
        *zzj*

        :param blocks_k: shape: (2**w, u)，2**w种情况下的u个块
        """
        def blocks_group_diff(blocks: np.ndarray) -> int:
            """
            遍历一组u个块，每一块的 sum(每一行与上一行像素值之差 + 每一列与上一列像素值之差) 之和。
            等价于
            u个块看作一整张8 x 8u的图片，计算sum(每一行与上一行像素值之差 + 每一列与上一列像素值之差)

            :param blocks: 一组u个块，shape: (8, 8*u)
            """
            def row_diff(blocks: np.ndarray):
                return np.sum(np.abs(blocks[1:] - blocks[:-1]))
            def col_diff(blocks: np.ndarray):
                return np.sum(np.abs(blocks[:,1:] - blocks[:,:-1]))
            rowDiff = row_diff(blocks)
            colDiff = col_diff(blocks)
            return rowDiff + colDiff

        # 把 List[List[Image.Image]] 转换为 ndarray, shape: (2**w, 8, 8*u)
        npblocks_k = [np.concatenate(blocks, axis=1) for blocks in blocks_k]  # 每个块转换为(8, 8*u) 的ndarray
        npblocks_k = [np.expand_dims(blocks, axis=0) for blocks in npblocks_k]  # 每个块增加一维，变为(1, 8, 8*u)
        npblocks_k = np.concatenate(npblocks_k, axis=0)  # shape: (2**w, 8, 8*u) 2**w个块叠加在一起
        # 计算所有2**w种情况下每组的blocks_group_diff
        block_diffs = np.asarray([blocks_group_diff(blocks) for blocks in npblocks_k])  # shape: (2**w)
        # 求最小的那一个的下标
        min_ind = np.argmin(block_diffs)
        return min_ind



