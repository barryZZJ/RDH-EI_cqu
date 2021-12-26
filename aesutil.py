import base64
import imgUil
from bitstring import BitStream
import json
from consts import *
from Crypto.Cipher import AES
import random

class AESUtil:
    __BLOCK_SIZE_16 = BLOCK_SIZE_16 = AES.block_size
    """加密解密相关操作"""
    def __init__(self, config: str):
        """
        如果config不为空则从配置文件初始化self.iv和self.key，
        否则随机初始化self.iv和self.key。
        :param config: 配置文件路径字符串
        """
        if config:
            self.iv, self.key = self.read_config(config)
        else:
            self.iv, self.key = self.rand_init()
        self.save_config()
        print(self.iv,self.key)
    def save_config(self, config: str = AES_CONFIG_PATH):
        """
        保存iv和key到配置文件中，可以考虑构建字典然后JSON.dump，则配置文件后缀名为.json
        :param config: 配置文件路径字符串
        """
        with open(config, "r", encoding="utf-8") as f:
            data = json.load(f)
        data['decode_iv'] = self.iv
        data['decode_key'] = self.key
        with open(config, "w") as f:
            json.dump(data, f, ensure_ascii=False)
    def read_config(self, config: str = AES_CONFIG_PATH):
        """
        从配置文件中读取iv和key，可以考虑用JSON.load读取字典
        :param config: 配置文件路径字符串
        """
        with open(config) as f:
            data = json.load(f)
        return [data['iv'], data['key']]
    def rand_init(self) :
        """随机初始化iv和key"""
        str = ''
        iv = str.join(random.choice("0123456789") for i in range(16))
        key = str.join(random.choice("0123456789") for i in range(16))
        return iv, key

    def encrypt(self, m: bytes) -> bytes:
        """对明文字节流m加密，返回密文字节流"""
        with open(AES_CONFIG_PATH) as f:
            data = json.load(f)
        key=(data['key']).encode()
        iv=(data['iv']).encode()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        print(type(m))

        str=bytes.decode(m)
        msg=cipher.encrypt(str)
        return msg

    def decrypt(self, c: bytes, iv: bytes = None) -> bytes:
        """
        对密文字节流c解密，返回明文字节流
        其他模块解密需要动态修改iv，因此提取为参数，默认使用self.iv即可
        """
        with open(AES_CONFIG_PATH) as f:
            data = json.load(f)
        key=data['decode_key']
        iv=data['decode_iv']
        cipher = AES.new(key, AES.MODE_CBC, iv)
        msg = cipher.decrypt(c)
        return msg

if __name__ == '__main__' :
    #test = AESUtil("")
    test = AESUtil(AES_CONFIG_PATH)
    bitplanes = imgUil.img_to_bitstream(PIC_8_PATH)
    print(bitplanes)
    bitplanes2 = test.encrypt(bitplanes)
    print(bitplanes2)
    bitplanes3 = test.decrypt(bitplanes2)
    print(bitplanes3)