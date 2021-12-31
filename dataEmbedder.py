import secrets
from bitstring import BitStream
from typing import List
from PIL import Image
from consts import *
from aesutil import AESUtil
from imgUil import segment_every, join
from imgUil import img_to_bitstream
import numpy as np
from numpy.typing import NDArray
import random

from Crypto.Cipher import AES

DEBUG = True


# ! 测试数据使用consts.py中的常量，有改动在consts.py中修改
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
        with open(config, 'wb') as f:
            f.write(self.key)

    def read_config(self, config: str = EMBED_CONFIG_PATH) -> bytes:
        """
        从配置文件中读取key，并返回key
        *yzy*

        :param config: 配置文件路径字符串
        """
        with open(config, 'rb') as f:
            key = f.read()
        return key

    def rand_init(self) -> bytes:
        """
        随机初始化key，并返回key。
        *yzy*
        """
        key = secrets.token_bytes(EMBED_KEY_LEN)
        return key

    def embed(self, data: bytes, img: bytes) -> bytes:
        """
        把字节流data嵌入到密文字节流img中，返回嵌入后的字节流
        """
        #TODO 检测嵌入数据量是否过大
        img = BitStream(bytes=img)  # 把img转为BitStream
        blocks_of_lsb = self.extract_lsb(img)  # 取出lsb, shape: (K), 大小64bit*K
        blocks_of_lsb = self.shuffle(blocks_of_lsb)  # 打乱lsb
        bitstream_LSB = join(blocks_of_lsb)
        K = len(blocks_of_lsb)
        L = K // EMBED_PARAM_U
        # 把bitstream_LSB分成L个组，每组包含了u个块的LSB，每组为64*u bit
        g = segment_every(bitstream_LSB, 64 * EMBED_PARAM_U)
        H = self.gen_matrix()
        # 把嵌入数据加密后data（l*w bits）分成l块，每块w bits,变成列表datas
        data = self.encrypt_data(data)
        data = BitStream(bytes=data)
        datas = segment_every(data, EMBED_PARAM_W)
        # 计算每一次的ak(w bits)和gk(64u bits)和rk(w bits)和vk（64u bits）
        v_groups = []
        for k in range(0, L):
            r_k = datas[k] ^ g[k][:EMBED_PARAM_W]
            v_k = self.dot(r_k, H) ^ g[k]
            v_groups.append(v_k)
        v = join(v_groups)  # 64*u * L
        img = self.sub_lsb(img, v)  # 把嵌入后的lsb放入原密文字节流的lsb中
        return img.bytes

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

    def extract_lsb(self, img: BitStream) -> List[BitStream]:
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

    def shuffle(self, blocks_of_lsb: List[BitStream]) -> List[BitStream]:
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

    def reverse_shuffle(self, blocks_of_lsb: List[BitStream]) -> List[BitStream]:
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

    def gen_matrix(self) -> NDArray[int]:
        """
        生成H=[I, Q]，其中Q用self.key随机初始化，返回矩阵H。
        *zt*

        :return: shape: (w, 64*u)
        """
        # 注：矩阵操作可能要用到numpy库
        # 先生成一个w*w的单位矩阵
        i = np.identity(EMBED_PARAM_W, dtype=int)
        # 再生成一个嵌入密钥控制的w*(64u-w)的二进制伪随机矩阵
        np.random.seed(int.from_bytes(self.key, byteorder='big', signed=False) % (2 ** 32 - 1))
        # 测试用np.random.seed(int.from_bytes(EMBED_KEY_DEBUG, byteorder='big', signed=False) % (2 ** 32 - 1))
        q = np.random.randint(0, 2, size=(EMBED_PARAM_W, (64 * EMBED_PARAM_U - EMBED_PARAM_W)))
        # 把i和q矩阵合并，成为一个w*64u的矩阵
        h = np.append(i, q, axis=1)
        return h

    def dot(self, bits: BitStream, matrix: NDArray[int]) -> BitStream:
        """
        比特流与矩阵点乘。
        FIXME: 目前为把bits转换为整数，相乘后转换回比特流。感觉效率最高的是生成Bits矩阵，比特之间直接相乘，但得手动实现。
        """
        bits = np.asarray(list(bits.bin), dtype=int)
        res = np.dot(bits, matrix)
        return BitStream(auto=res) # int列表自动识别为二进制流

    def encrypt_data(self, data: bytes) -> bytes:
        """
        对要嵌入的数据用self.key加密，且输入长度与输出长度相同。
        *yzy*
        """
        aes = AES.new(self.key, AES.MODE_ECB)
        if len(data) % 16 != 0:
            # 填充至16字节的倍数
            data += b'\0' * (16 - len(data) % 16)
        ciphertext = aes.encrypt(data)
        return ciphertext

    def decrypt_data(self, data: bytes) -> bytes:
        """
        对要提取出的数据用self.key解密。
        *yzy*
        """
        aes = AES.new(self.key, AES.MODE_ECB)
        message = aes.decrypt(data)
        message = message.rstrip(b'\0')
        return message

    def sub_lsb(self, img: BitStream, sub: BitStream) -> BitStream:
        """
        把img中每一块的LSB替换为sub。根据实际情况sub可以改为List[BitStream]。
        *zt*
        """
        # 每一个块是64b*8=512bit，每个块的前64bit就是每块的LSB
        segs = segment_every(img, 512)
        subs = segment_every(sub, 64)
        for i in range(len(segs)):
            # 用sub列表的每一个元素（64bits）替换img每块的前64bits
            segs[i][:64] = subs[i]
        img = join(segs)
        return img

    def sub_group_lsb(self, imgk: BitStream, sub: BitStream) -> BitStream:
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
    #TODO
    # 1. lsb
    # 2. decrypt data
    # 3. 内部函数
    # 4. 静态函数
    # 5. extract
    # 6. 参数w, u与图片和信息量自动适配 + data自动填充至所需长度
    de = DataEmbedder()
    img = img_to_bitstream(PIC_128_PATH)
    data = EMBED_DATA_DEBUG  # 128bit, u=2, w=1 时适合嵌入128x128图片
    nimg = de.embed(data, img.bytes)