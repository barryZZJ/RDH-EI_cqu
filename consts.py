# 各种常量，方便写GUI和Main时直接使用
AES_CONFIG_PATH = "aesConf.key"  # 加密相关配置文件默认存储路径
EMBED_CONFIG_PATH = "embedConf.json"  # 信息嵌入相关配置文件默认存储路径
PIC_512_PATH = "pics/lena512.bmp"  # 测试用图片路径, 512x512
PIC_128_PATH = "pics/lena128.bmp"  # 测试用图片路径, 128x128
PIC_8_PATH = "pics/lena8.bmp"  # 测试用图片路径, 8x8
PIC_8_2_PATH = "pics/lena8_2.bmp"  # 测试用图片路径, 8x8


PIC_16_PATH = "pics/lena16.bmp"  # 嵌入信息测试用图片，16x16
# TODO 下面这些最后放到dataEmbedder.py里
EMBED_KEY_LEN = 16  # 嵌入密钥长度，字节数
EMBED_KEY_DEBUG = bytes.fromhex('a9ed88811c8a7864283fde603abd5132')  # 默认密钥。16字节 = 128比特。考虑到数据加密使用AES，密钥也应该是字节。
EMBED_PARAM_W = 1
EMBED_PARAM_U = 2
EMBED_DATA_DEBUG = b'testtesttesttest'