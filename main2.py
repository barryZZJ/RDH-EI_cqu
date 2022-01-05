import os
from PIL import Image

from bitstring import BitStream
from aesutil import AESUtil
from dataEmbedder import DataEmbedder, DataExtractor
from imgUil import img_to_bitstream, bitstream_to_img, evaluate_psnr
from consts import *

# init
aes = AESUtil()
if os.path.exists(AES_CONFIG_PATH):
    aes.load_config(AES_CONFIG_PATH)
aes.save_config(AES_CONFIG_PATH)
demb = DataEmbedder()
dext = DataExtractor()

# load pic
test_pic_path = PIC_512_PATH
test_pic_save_path = 'results/ori.bmp'
test_picenc_save_path = 'results/encrypt.bmp'
test_picemb_save_path = 'results/embed.bmp'
test_picnois_save_path = 'results/noise.bmp'
test_picperf_save_path = 'results/perf.bmp'
test_data_path = 'results/data.txt'
test_dataext_path = 'results/extracted_data.txt'
img_ori = Image.open(test_pic_path).convert(mode='L')
img_ori.save(test_pic_save_path)

bs = img_to_bitstream(test_pic_path)
# load data
data = demb.read_data(test_data_path)

# 配置data embedder
if os.path.exists(EMBED_CONFIG_PATH):
    # load params from config file
    demb.load_config(EMBED_CONFIG_PATH)
else:
    # optimize params using pic and data
    demb.optimize_params(len(data) * 8, len(bs.bytes) * 8)
# 保存配置文件
demb.save_config(EMBED_CONFIG_PATH)

# 配置 data extractor
dext.load_config(EMBED_CONFIG_PATH, aes)
# 加密原图
b_c = aes.encrypt(bs.bytes)  # bytes_cipher
# 保存图片
bitstream_to_img(BitStream(b_c)).save(test_picenc_save_path)

# 嵌入信息
b_c_mk = demb.embed(data, b_c)  # bytes_cipher_marked
# 保存图片
bitstream_to_img(BitStream(b_c_mk)).save(test_picemb_save_path)

# 提取信息
data_ext = dext.extract(b_c_mk)  # data_extracted
print("extracted:",data_ext.decode('utf8'))
dext.save_data(data_ext, test_dataext_path)

# 有损解密
b_m_nois = aes.decrypt(b_c_mk)  # bytes_msg_noisy
# 保存图片
img_nois = bitstream_to_img(BitStream(b_m_nois))
img_nois.save(test_picnois_save_path)

# 无损解密，需要输入提取出的文本
img_perf = dext.perfect_decrypt(data_ext, b_c_mk)
img_perf.save(test_picperf_save_path)

psnr_nois = evaluate_psnr(img_nois, img_ori)
psnr_perf = evaluate_psnr(img_perf, img_ori)
print("psnr of noisy img:\n", psnr_nois)
print("psnr of perfect img:\n", psnr_perf)
