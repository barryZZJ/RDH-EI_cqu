from typing import List
import math
import numpy as np
from numpy.typing import NDArray
from PIL import Image
from bitstring import BitStream
from consts import *
from imgUil import img_to_bitstream, bitstream_to_img

def img_to_bitstream_np(filepath: str) -> BitStream:
    """输入图片路径，返回编码后的字节流，即论文中的b"""
    img = Image.open(filepath)  # type: Image.Image  # 用PIL打开图片，得到Image对象
    # FIXME 目前只支持灰度图
    img = img.convert(mode="L")
    img = np.asarray(img)
    blocks = _to_blocks_np(img)  # 分成K个8x8的块 (论文中Oi)
    list_of_bitplanes = []  # 所有位平面列表构成的列表 (论文中b), 512*K bit。一个位平面列表是论文中的bi, 64bit * 8 = 512 bit；一个位平面是论文中的bi^(k), 64 bit。
    for block in blocks:
        bitplanes = _block_to_bitplanes_np(block)  # 把一个块转换成位平面列表(论文中bi), 512 bit
        list_of_bitplanes.append(bitplanes)

    bitstream = join(list_of_bitplanes)  # 把列表合并成比特流
    return bitstream

def _to_blocks_np(img: NDArray[int]) -> List[NDArray[int]]:
    """把图片拆分成K个块 (Oi, 8x8=64个像素)，并作为列表返回"""
    N, M = img.shape[0]//8, img.shape[1]//8
    blocks = []
    row_blocks = np.vsplit(img, N)  # 按行切分成N块
    for row_block in row_blocks:
        blocks.extend(np.hsplit(row_block, M))  # 每个行块按列切分成M块
    return blocks

def _block_to_bitplanes_np(block: NDArray[int]) -> BitStream:
    """
    把一个块 (64个像素) 转换成位平面列表(论文中bi) (64bit*8=512bit)。
    一个位平面是论文中的bi^(k), 64 bit。
    """
    # 把每个像素点转换成二进制
    pixels = [] # type: List[BitStream] # 共64个像素点
    for pixel in block.flatten():
        pixels.append(BitStream(uint=pixel, length=8))  # 8位无符号整数
    # 生成bitplanes，即论文中的向量组bi，64bit * 8 = 512 bit
    bitplanes = []
    for k in range(-1, -8 - 1, -1):
        # 把每个像素点的第k位取出来组成一个bitplane，即论文中的bi^(k)，64 bit
        bitplane = BitStream()
        for pixel in pixels:  # 64个像素
            bitplane += BitStream(bool=pixel[k])  # k=-1即第0位(最低位)，-2即第1位，以此类推
        bitplanes.append(bitplane)

    bitplanes = join(bitplanes)  # 把列表合并成比特流
    return bitplanes

def segment_every(bitstream: BitStream, bits: int) -> List[BitStream]:
    """
    比特流b，每bits个比特为一组，组成一个列表。
    如bits=128时，把bitstream分成128bit一组，每个元素即si^(j)就是一个128 bit的BitStream，用于输入加密器。
    bits=64u时，分组用于嵌入信息。

    注：加密器使用该输出时，可以通过列表里每个BitStream对象的bytes成员(如bitstream.bytes)把BitStream对象转换为字节。
    """
    list_of_bitplanes = []
    for k in range(0, len(bitstream)//bits):
        list_of_bitplanes.append(bitstream[k*bits:(k+1)*bits])
    return list_of_bitplanes

def join(seg: List[BitStream]) -> BitStream:
    """
    把列表的每个元素合并成一个完整的字节流

    注：输入字节密文列表时，要先把列表里每个密文字节转换成BitStream，可以通过BitStream(bytes=密文字节)实现
    """
    return BitStream().join(seg)

def bitstream_to_img_np(bitstream: BitStream) -> Image.Image:
    """输入密文字节流e，计算对应像素值，解码为图片，即img_to_bitstream的逆过程。"""
    blocks = _bitstream_to_blocks_np(bitstream)
    img = _from_blocks_np(blocks)
    # FIXME 目前只支持灰度图
    img = Image.fromarray(img, mode='L')
    #! 如果有需要可以添加保存到本地的函数
    return img

def _bitstream_to_blocks_np(bitstream: BitStream) -> List[NDArray[int]]:
    """输入密文字节流e，计算对应像素值，解码为各个图片块，不需要拼接"""
    list_of_bitplanes = segment_every(bitstream, 512)  # 分成K个512 bits的列表，每个元素是一个块的位平面列表
    blocks = []
    for bitplanes in list_of_bitplanes:
        block = _bitplanes_to_block_np(bitplanes)
        blocks.append(block)
    return blocks

def _bitplanes_to_block_np(bitplanes: BitStream) -> NDArray[int]:
    """把512bit的位平面列表bitplanes (论文中bi) 重构为一个块 (Oi, 64个像素)"""
    #把bit流，分为8*64记录每个像素的内容
    bitplanes2=BitStream()
    for x in range(0,64):
        for y in range(0,8):
            bitplanes2 += BitStream(bool=bitplanes[x+64*(7-y)])
    list_of_pixels = segment_every(bitplanes2, 8)
    block = np.asarray([pixel.uint for pixel in list_of_pixels])
    block = block.reshape(8, 8)
    return block

def _from_blocks_np(blocks: List[NDArray[int]]) -> NDArray[int]:
    """把图片分块合并成一个完整的图片，注意返回的是Image对象"""
    # 可使用Image.Image的paste方法
    # FIXME 目前只实现正方形图片
    N = int(len(blocks) ** 0.5)
    rows = []
    for i in range(N):
        # 按列合并成行块
        rows.append(np.hstack(blocks[i*N: (i+1)*N]))
    # 把行块合并成整块
    img = np.vstack(rows)
    return img

def evaluate_psnr(decrypted: Image.Image, original: Image.Image):
    """
    计算解密后的图片与原图的PSNR值，评估解密图片的效果
    """
    # img1 and img2 have range [0, 255]
    img1 = np.asarray(decrypted, dtype=np.float64)
    img2 = np.asarray(original, dtype=np.float64)
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return np.inf
    PIXEL_MAX = 255.0
    return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))


if __name__ == '__main__':
    import time
    st = time.time()
    bs = img_to_bitstream(PIC_512_PATH)
    print('img_to_bs:', time.time()-st)
    st = time.time()
    img=bitstream_to_img(bs)
    print('bs_to_img:', time.time()-st)

    st = time.time()
    bs2 = img_to_bitstream_np(PIC_512_PATH)
    print('img_to_bs_np:', time.time()-st)
    st = time.time()
    img2=bitstream_to_img_np(bs2)
    print('bs_to_img_np:', time.time()-st)

