import os
from bitstring import BitStream

from aesutil import AESUtil
from dataEmbedder import DataEmbedder, DataExtractor
from imgUil import img_to_bitstream, bitstream_to_img
from consts import *

# init
# aesUtil
aes = AESUtil()
if os.path.exists(AES_CONFIG_PATH):
    aes.load_config(AES_CONFIG_PATH)
aes.save_config(AES_CONFIG_PATH)

# load pic
test_pic_path = PIC_128_PATH
bs = img_to_bitstream(test_pic_path)
# load data
data = 'testtesttesttest'.encode('utf8')

# DataEmbedder和DataExtractor都继承了DataUtil，DataUtil包含读取和保存配置文件
# 配置data embedder
demb = DataEmbedder()
if os.path.exists(EMBED_CONFIG_PATH):
    # load params from config file
    demb.load_config(EMBED_CONFIG_PATH)
else:
    # optimize params using pic and data
    demb.optimize_params(len(data) * 8, len(bs.bytes) * 8)
# 保存配置文件
demb.save_config(EMBED_CONFIG_PATH)

# 配置 data extractor
dext = DataExtractor(EMBED_CONFIG_PATH, AES_CONFIG_PATH)

# 加密原图
b_c = aes.encrypt(bs.bytes)  # bytes_cipher

# 嵌入信息
b_c_mk = demb.embed(data, b_c)  # bytes_cipher_marked

# 提取信息
data_ext = dext.extract(b_c_mk)  # data_extracted
print(data_ext.decode('utf8'))

# 有损解密
b_m_nois = aes.decrypt(b_c_mk)  # bytes_msg_noisy
# 保存图片
img = bitstream_to_img(BitStream(b_m_nois))
img.save('noisy_pic.jpg')

# 无损解密，需要输入提取出的文本
b_m_perf = dext.perfect_decrypt(data_ext, b_c_mk)  # bytes_msg_perfect
img.save('perfect_pic.jpg')
