import math
import numpy as np
from numpy.typing import NDArray
import random
import secrets
from bitstring import BitStream
from typing import List, Tuple
from PIL import Image
from Crypto.Cipher import AES

from consts import *
from aesutil import AESUtil
from imgUil import segment_every, join, _bitstream_to_blocks, _from_blocks
# ! 测试数据使用consts.py中的常量，有改动在consts.py中修改


class DataLongError(BaseException):
    """用于嵌入数据量较大，无法保证无损恢复原图时的报错，当作Warning处理，在GUI中弹出提示即可"""
    pass


class DataUtil:
    """公共处理函数，主要为实现细节"""
    key: bytes
    PARAM_U: int
    PARAM_W: int

    def save_config(self, config: str = EMBED_CONFIG_PATH):
        """
        保存key、参数U、W到配置文件中
        *yzy*

        :param config: 配置文件路径字符串
        """
        with open(config, 'wb') as f:
            f.write(self.key)
            f.write(b'\0')
            f.write(str(self.PARAM_U).encode('utf8'))
            f.write(b'\0')
            f.write(str(self.PARAM_W).encode('utf8'))

    @staticmethod
    def _read_config(config: str = EMBED_CONFIG_PATH) -> Tuple[bytes, int, int]:
        """
        从配置文件中读取key、参数U、W，并返回
        *yzy*

        :param config: 配置文件路径字符串
        """
        with open(config, 'rb') as f:
            key, u, w = f.read().split(b'\0')
        u = int(u.decode('utf8'))
        w = int(w.decode('utf8'))
        return key, u, w

    def load_config(self, config: str = EMBED_CONFIG_PATH):
        self.key, self.PARAM_U, self.PARAM_W = self._read_config(config)

    @staticmethod
    def read_data(file_path: str) -> bytes:
        with open(file_path, 'rb') as f:
            data = f.read()
        return data

    @staticmethod
    def save_data(data: bytes, file_path: str):
        with open(file_path, 'wb') as f:
            f.write(data)

    def optimize_params(self, data_bits: int, img_bits: int):
        """
        为了优化嵌入效果，根据data和图片大小动态调整参数W和U，自动确定最合适的参数组合

        :return: (u, w)
        """
        # w越小 u越大 效果越好
        # len(data) == K // u * w
        K = img_bits // 512
        data_bits = math.ceil(data_bits/128)*128
        # 选第一个满足data长度的组合
        for u, w in DataEmbedder.PARAM_PAIRS['perf']:
            if data_bits <= K // u * w:
                self.PARAM_U = u
                self.PARAM_W = w
                return
        for u, w in DataEmbedder.PARAM_PAIRS['noisy']:
            if data_bits <= K // u * w:
                self.PARAM_U = u
                self.PARAM_W = w
                raise DataLongError("嵌入数据量较大，无法保证无损恢复原图！")
        raise ValueError("嵌入数据量过大，嵌入信息失败！")

    @staticmethod
    def _pad_data(data: bytes, seg_bits: int) -> bytes:
        """填充data，使其长度至少达到 L*w = K//u*w 位"""
        seg_len = seg_bits // 8
        if len(data) % seg_len != 0:
            data += b'\0' * (seg_len - len(data) % seg_len)
        return data

    @staticmethod
    def _strip_padding(data: bytes) -> bytes:
        """去除填充"""
        data = data.rstrip(b'\0')
        return data

    def _shuffle(self, blocks_of_lsb: List[BitStream]) -> List[BitStream]:
        """
        打乱列表里的每个元素，要求算法可逆，密钥使用self.key。

        :param blocks_of_lsb: 以每块的LSB构成的列表

        *zt*
        """
        # 使用self.key作为种子设置random,然后生成一个K长度的随机数列
        random.seed(self.key)
        N = len(blocks_of_lsb)
        rlist = random.sample(range(0, N), k=N)
        # 然后按照随机数列给原数列打乱
        new_blocks_of_lsb = []
        for i in range(0, len(blocks_of_lsb)):
            new_blocks_of_lsb.append(blocks_of_lsb[rlist[i]])
        return new_blocks_of_lsb

    def _reverse_shuffle(self, blocks_of_lsb: List[BitStream]) -> List[BitStream]:
        """
        上面算法的逆。

        :param blocks_of_lsb: 以每块的LSB构成的列表

        *zt*
        """
        # 使用self.key作为种子设置random,然后生成一个K长度的随机数列，再把这个数列的逆数列求出来
        random.seed(self.key)
        N = len(blocks_of_lsb)
        rlist = random.sample(range(0, N), k=N)
        rrlist = [0] * N
        for i in range(0, len(blocks_of_lsb)):
            rrlist[rlist[i]] = i
        # 然后按照逆随机数列把打乱数列还原
        new_blocks_of_lsb = []
        for i in range(0, len(blocks_of_lsb)):
            new_blocks_of_lsb.append(blocks_of_lsb[rrlist[i]])
        return new_blocks_of_lsb

    @staticmethod
    def _extract_lsb(img: BitStream) -> List[BitStream]:
        """
        提取出每块的LSB，组成列表。[c0^(0), c1^(0),...,ck-1^(0)]。共64bit * K

        *zt*
        """
        # 每一个块是64b*8=512bit
        segs = segment_every(img, 512)
        # 每个块的前64bit就是每块的LSB
        lsbs = []  # 全部块的LSB列表
        for i in range(len(segs)):
            lsbs.append(segs[i][:64])
        return lsbs

    def _gen_matrix(self) -> NDArray[int]:
        """
        生成H=[I, Q]，其中Q用self.key随机初始化，返回矩阵H。
        *zt*

        :return: shape: (w, 64*u)
        """
        # 注：矩阵操作可能要用到numpy库
        # 先生成一个w*w的单位矩阵
        i = np.identity(self.PARAM_W, dtype=int)
        # 再生成一个嵌入密钥控制的w*(64u-w)的二进制伪随机矩阵
        np.random.seed(int.from_bytes(self.key, byteorder='big', signed=False) % (2 ** 32 - 1))
        # 测试用np.random.seed(int.from_bytes(EMBED_KEY_DEBUG, byteorder='big', signed=False) % (2 ** 32 - 1))
        q = np.random.randint(0, 2, size=(self.PARAM_W, (64 * self.PARAM_U - self.PARAM_W)))
        # 把i和q矩阵合并，成为一个w*64u的矩阵
        h = np.append(i, q, axis=1)
        return h

    @staticmethod
    def _dot(bits: BitStream, matrix: NDArray[int]) -> BitStream:
        """
        比特流与矩阵点乘。
        FIXME: 目前为把bits转换为整数，相乘后转换回比特流。感觉效率最高的是生成Bits矩阵，比特之间直接相乘，但得手动实现。
        """
        bits = np.asarray(list(bits.bin), dtype=int)
        res = np.dot(bits, matrix)
        return BitStream(auto=res)  # int列表自动识别为二进制流

    def _encrypt_data(self, data: bytes) -> bytes:
        """
        对要嵌入的数据用self.key加密，且输入长度与输出长度相同。
        *yzy*
        """
        aes = AES.new(self.key, AES.MODE_ECB)
        if len(data) % 16 != 0:
            data += b'\1' * (16 - len(data) % 16)
        ciphertext = aes.encrypt(data)
        return ciphertext

    def _decrypt_data(self, data: bytes) -> bytes:
        """
        对要提取出的数据用self.key解密。
        *yzy*
        """
        aes = AES.new(self.key, AES.MODE_ECB)
        message = aes.decrypt(data)
        message = message.rstrip(b'\1')
        return message

    @staticmethod
    def _sub_lsb(img: BitStream, sub: BitStream) -> BitStream:
        """
        把img中每一块的LSB替换为sub。根据实际情况sub可以改为List[BitStream]。
        *zt*
        """
        # 每一个块是64b*8=512bit，每个块的前64bit就是每块的LSB
        segs = segment_every(img, 512)
        subs = segment_every(sub, 64)
        # len(subs) <= len(segs)，所以i取0~len(subs)-1
        for i in range(len(subs)):
            # 用sub列表的每一个元素（64bits）替换img每块的前64bits
            segs[i][:64] = subs[i]
        img = join(segs)
        return img

    @staticmethod
    def _sub_group_lsb(imgk: BitStream, sub: BitStream) -> BitStream:
        """
        把img中的一组u个块的LSB替换为sub。考虑sub_LSB能否直接实现。
        *zzj*

        :param imgk: size=64b*8 *u
        :param sub: size=64b *u
        """
        return DataEmbedder._sub_lsb(imgk, sub)


class DataEmbedder(DataUtil):
    """信息嵌入相关操作"""
    # 可选参数组合：保证psnr的前提下，按嵌入量从小到大排序
    # (U, W)
    PARAM_PAIRS = {
        'perf': sorted([
            (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8),
            (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
            (2, 1)
        ], key=lambda pair: pair[1]/pair[0]),
        'noisy': list((4, w) for w in range(9, 17))
    }

    def __init__(self, config: str = None):
        """
        如果config不为空则从配置文件初始化self.key，否则随机初始化self.key。
        *yzy*

        :param config: 配置文件路径字符串
        """
        if config:
            self.key, self.PARAM_U, self.PARAM_W = self._read_config(config)
        else:
            self.key = self._rand_init()
            # 默认选择无损情况下可嵌入量最高的参数组合
            self.PARAM_U, self.PARAM_W = self.PARAM_PAIRS['perf'][-1]

    @staticmethod
    def _rand_init() -> bytes:
        """
        随机初始化key，并返回key。
        *yzy*
        """
        key = secrets.token_bytes(EMBED_KEY_LEN).replace(b'\0', b'\x01')
        return key

    def embed(self, data: bytes, img: bytes) -> bytes:
        """
        把字节流data嵌入到密文字节流img中，返回嵌入后的字节流
        """
        img = BitStream(bytes=img)  # 把img转为BitStream
        blocks_of_lsb = self._extract_lsb(img)  # 取出lsb, shape: (K), 大小64bit*K
        bitstream_lsb = join(blocks_of_lsb)
        K = len(blocks_of_lsb)
        L = K // self.PARAM_U
        # 把bitstream_LSB分成L个组，每组包含了u个块的LSB，每组为64*u bit
        g = segment_every(bitstream_lsb, 64 * self.PARAM_U)[:L]  # 考虑到K如果不能整除U，则丢弃达不到64u bit的最后一组
        H = self._gen_matrix()
        # 把嵌入数据data加密后（填充至l*w bits）分成l块，每块w bits,变成列表datas
        data = self._encrypt_data(data)
        # 填充data至L*w bits
        data = self._pad_data(data, L*self.PARAM_W)
        data = BitStream(bytes=data)
        datas = segment_every(data, self.PARAM_W)
        # 计算每一次的ak(w bits)和gk(64u bits)和rk(w bits)和vk（64u bits）
        v_groups = []  # 64*u * L
        for k in range(L):
            r_k = datas[k] ^ g[k][:self.PARAM_W]
            v_k = self._dot(r_k, H) ^ g[k]
            v_groups.append(v_k)
        v = join(v_groups)
        img = self._sub_lsb(img, v)  # 把嵌入后的lsb放入原密文字节流的lsb中
        return img.bytes


class DataExtractor(DataUtil):
    """信息提取相关操作"""
    def __init__(self, config, aesconfig: str = None):
        """
        如果config不为空则从配置文件初始化self.key，否则随机初始化self.key。
        如果aesconfig不为空，初始化AESUtil，用于完美解密图片。
        *yzy*

        :param config: 配置文件路径字符串
        :param aesconfig: 加解密相关配置文件路径字符串
        """
        self.key, self.PARAM_U, self.PARAM_W = self._read_config(config)

        if aesconfig:
            self.aes = AESUtil(aesconfig)
        else:
            self.aes = None

    def extract(self, img: bytes) -> bytes:
        """
        从字节流img中提取信息，返回提取出的信息字节流
        *yzy*
        """
        try:
            assert self.key is not None
        except AssertionError:
            raise ValueError("未加载嵌入密钥配置文件")
        img = BitStream(bytes=img)
        blocks_of_lsb = self._extract_lsb(img)
        bitstream_lsb = join(blocks_of_lsb)
        K = len(blocks_of_lsb)
        L = K // self.PARAM_U
        g = segment_every(bitstream_lsb, 64 * self.PARAM_U)[:L]  # 考虑到K如果不能整除U，则丢弃达不到64u bit的最后一组
        datas = []
        for k in range(L):
            datas.append(g[k][:self.PARAM_W])
        data = join(datas).bytes
        data = self._strip_padding(data)
        data = self._decrypt_data(data)
        return data

    def perfect_decrypt(self, data: bytes, img: bytes) -> Image.Image:
        """
        如果同时拥有加密密钥和嵌入密钥，可以无损解密原始图片。
        需要调用AESUtil相关功能。
        我认为应该由信息嵌入器进行处理，因为该功能只有信息嵌入者知道。

        *zzj*
        """
        try:
            assert self.key is not None
        except AssertionError:
            raise ValueError("未加载嵌入密钥配置文件")
        try:
            assert isinstance(self.aes, AESUtil)
        except AssertionError:
            raise ValueError("未加载解密密钥配置文件")
        img = BitStream(bytes=img)
        blocks_of_lsb = DataEmbedder._extract_lsb(img)
        bitstream_lsb = join(blocks_of_lsb)
        K = len(blocks_of_lsb)
        L = K//self.PARAM_U
        # 把bitstream_lsb分成L个组，每组包含了u个块的LSB，每组为64*u bit
        g = segment_every(bitstream_lsb, 64*self.PARAM_U)[:L]  # 考虑到K如果不能整除U，则丢弃达不到64u bit的最后一组
        H = self._gen_matrix()
        data = self._encrypt_data(data)
        data = self._pad_data(data, L*self.PARAM_W)
        data = BitStream(bytes=data)
        datas = segment_every(data, self.PARAM_W)
        # 以组为单位，尝试恢复 gk
        # 恢复原理：遍历 gk[:w]所有可能的取值，全部解密出原图（共w位，故2^w个图），通过数字统计关系选出最合理的那一个
        best_blocks = []
        e_grouped = segment_every(img, 512*self.PARAM_U)  # u个块(64b*8 * u)一组，共L组
        iv = None
        for k in range(0, L-1 + 1):
            blocks_k = [None] * (2**self.PARAM_W)  # type: List[List[Image.Image]] # shape: (2^w, u)
            # blocks_k[l] = 第k组中，第l种情况的u个块
            e_k = e_grouped[k].copy()  # FIXME 能否删除copy
            for l in range(2**self.PARAM_W):
                t_l = BitStream(uint=l, length=self.PARAM_W)
                r_k = datas[k] ^ t_l
                w_k = g[k] ^ self._dot(r_k, H)
                e_k = self._sub_group_lsb(e_k, w_k)  # 把e_k的LSB替换为w_k，即论文中的r
                m = self.aes.decrypt(e_k.bytes, iv=iv)  # 只解密第k组的u个块，iv为上一组的最后128bit
                m = BitStream(bytes=m)
                P_kl = _bitstream_to_blocks(m)  # u个8x8的像素块列表
                blocks_k[l] = P_kl  # 记录第l种情况下的u个块
            iv = e_grouped[k][-128:].bytes
            best_l = self._optimize(blocks_k)  # 正确性已检查
            best_blocks.extend(blocks_k[best_l])  # 最合理的u个块添加到结果中
        best_img = _from_blocks(best_blocks)
        return best_img

    @staticmethod
    def _optimize(blocks_k: List[List[Image.Image]]) -> int:
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
                return np.sum(np.abs(blocks[:, 1:] - blocks[:, :-1]))

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

