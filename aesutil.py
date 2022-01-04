from typing import Tuple
from bitstring import BitStream
from consts import *
from Crypto.Cipher import AES
import secrets
import imgUil

class AESUtil:
    __BLOCK_SIZE_16 = BLOCK_SIZE_16 = AES.block_size
    """加密解密相关操作"""
    def __init__(self, config: str = None):
        """
        如果config不为空则从配置文件初始化self.iv和self.key，
        否则随机初始化self.iv和self.key。
        :param config: 配置文件路径字符串
        """
        if config:
            self.iv, self.key = self._read_config(config)
        else:
            self.iv, self.key = self._rand_init()

    def save_config(self, config: str = AES_CONFIG_PATH):
        """
        保存iv和key到配置文件中
        :param config: 配置文件路径字符串
        """
        with open(config, "wb") as f:
            f.writelines([
                self.iv,
                b'\0',
                self.key
            ])

    @staticmethod
    def _read_config(self, config: str = AES_CONFIG_PATH) -> Tuple[bytes, bytes]:
        """
        从配置文件中读取iv和key
        :param config: 配置文件路径字符串
        """
        with open(config, "rb") as f:
            iv, key = f.read().split(b'\0')
        return iv, key

    def load_config(self, config: str = AES_CONFIG_PATH):
        """
        从配置文件中读取iv和key并加载为成员属性。
        """
        self.iv, self.key = self._read_config(config)

    @staticmethod
    def _rand_init() -> Tuple[bytes, bytes]:
        """随机初始化iv和key"""
        iv = secrets.token_bytes(16).replace(b'\0', b'\x01') # 避免出现分隔符，方便读取文件
        key = secrets.token_bytes(16).replace(b'\0', b'\x01')
        return iv, key

    def encrypt(self, m: bytes) -> bytes:
        """对明文字节流m加密，返回密文字节流"""
        iv = self.iv
        key = self.key
        cipher = AES.new(key, AES.MODE_CBC, iv)
        msg = cipher.encrypt(m)
        return msg

    def decrypt(self, c: bytes, iv: bytes = None) -> bytes:
        """
        对密文字节流c解密，返回明文字节流
        其他模块解密需要动态修改iv，因此提取为参数，默认使用self.iv即可
        """
        if not iv:
            iv = self.iv
        key = self.key
        cipher = AES.new(key, AES.MODE_CBC, iv)
        msg = cipher.decrypt(c)
        return msg

if __name__ == '__main__' :
    test = AESUtil()
    bitplanes = imgUil.img_to_bitstream(PIC_512_PATH)
    #print(bitplanes)
    bitplanes2 = test.encrypt(bitplanes.bytes)
    #print(bitplanes2.hex())
    iv = test.iv
    bitplanes3 = test.decrypt(bitplanes2)
    #print(bitplanes3.hex())
    bitplanes3 = BitStream(bytes=bitplanes3)
    pic = imgUil.bitstream_to_img(bitplanes3)
    pic.show()