import os
from bitstring import BitStream
from PIL import Image
import numpy as np
from imgUil import img_to_bitstream, bitstream_to_img, evaluate_psnr, segment_every, join
from aesutil import AESUtil
from dataEmbedder import DataEmbedder, DataExtractor
from consts import *

PATH_BASE = 'result'
PATH = {
    'create': lambda : os.makedirs(PATH_BASE, exist_ok=True),
    'm': os.path.join(PATH_BASE, 'message_original.bmp'),
    'c': os.path.join(PATH_BASE, 'cipher.bmp'),
    'c_mk': os.path.join(PATH_BASE, 'cipher_marked.bmp'),
    'm_nois': os.path.join(PATH_BASE, 'message_noisy.bmp'),
    'm_perf': os.path.join(PATH_BASE, 'message_perfect.bmp'),
    'data': os.path.join(PATH_BASE, 'extracted_data.txt'),
    'psnr': os.path.join(PATH_BASE, 'psnr.txt'),
    'bs' : os.path.join(PATH_BASE, 'bs.hex'),
}

def save_img(bs: bytes, path):
    bs = BitStream(bytes=bs)
    img = bitstream_to_img(bs)
    img.save(path)
    return img

def save_data(dataori: bytes, dataext:bytes, path):
    if dataori != dataext: return
    with open(path, 'w') as f:
        f.write(dataext.decode('utf8'))

# init
PATH['create']()
aes = AESUtil()
if os.path.exists(AES_CONFIG_PATH):
    aes.load_config(AES_CONFIG_PATH)
aes.save_config(AES_CONFIG_PATH)
demb = DataEmbedder()
data = 'test'.encode('utf8')
test_pic_path = PIC_512_PATH

img_m = Image.open(test_pic_path).convert(mode='L')
img_m.save(PATH['m'])

# encrypt
if os.path.exists(PATH['bs']):
    with open(PATH['bs'], 'rb') as f:
        bs = f.read()
    bs = BitStream(bytes=bs)
else:
    bs = img_to_bitstream(test_pic_path)
    with open(PATH['bs'], 'wb') as f:
        f.write(bs.bytes)

if os.path.exists(EMBED_CONFIG_PATH):
    demb.load_config(EMBED_CONFIG_PATH)
else:
    demb.optimize_params(len(data) * 8, len(bs.bytes) * 8)
    # demb.PARAM_U = 2
    # demb.PARAM_W = 1

print('U =', demb.PARAM_U, ', W =', demb.PARAM_W)
demb.save_config(EMBED_CONFIG_PATH)
dext = DataExtractor(EMBED_CONFIG_PATH, AES_CONFIG_PATH)


def encrypt_img(bs: bytes, save=False)->bytes:
    bs_c = aes.encrypt(bs)
    if save:
        save_img(bs_c, PATH['c'])
    return bs_c

def embed_img(data:bytes, bs_c:bytes, save=False)->bytes:
    # embed
    bs_c_mk = demb.embed(data, bs_c)
    if save:
        save_img(bs_c_mk, PATH['c_mk'])
    return bs_c_mk

def extract_data(bs_c_mk: bytes) -> bytes:
    # extract
    data_ext = dext.extract(bs_c_mk)
    print(data_ext.decode('utf8'))
    return data_ext

def decrypt_img(bs_c_mk:bytes)->Image.Image:
    # decrypt_noisy
    bs_m_nois = aes.decrypt(bs_c_mk)
    img_m_nois = save_img(bs_m_nois, PATH['m_nois'])
    return img_m_nois

def decrypt_perfect(data_ext:bytes, b_c_mk:bytes)->Image.Image:
    # decrypt_perfect
    img_m_perf = dext.perfect_decrypt(data_ext, b_c_mk)
    img_m_perf.save(PATH['m_perf'])
    return img_m_perf

def psnr(img_m_dec):
    # psnr
    img_m = Image.open(test_pic_path).convert(mode='L')
    return evaluate_psnr(img_m_dec, img_m)


def full():
    b_c=encrypt_img(bs.bytes)
    b_c_mk=embed_img(data, b_c)
    data_ext=extract_data(b_c_mk)
    img_m_nois = decrypt_img(b_c_mk)
    img_m_perf = decrypt_perfect(data_ext, b_c_mk)
    res_noi = psnr(img_m_nois)
    res_per = psnr(img_m_perf)
    print('noisy:',res_noi)
    print('perfe:',res_per)

full()
