from typing import List
from PIL import Image
from bitstring import BitStream
from consts import *

def img_to_bitstream(filepath: str) -> BitStream:
    """输入图片路径，返回字节流，即论文中的b"""
    img = Image.open(filepath)  # type: Image.Image  # 用PIL打开图片，得到Image对象
    blocks = to_blocks(img)  # type: List[Image.Image]  # 分成K个8x8的块，即论文中的Oi, 长度为K
    bitstream = []  # 所有分块转换得到的比特流，即论文中的b, 512*K bit
    for block in blocks:
        bitplanes = to_bitplanes(block)  # 把一个块转换成bitplanes，即论文中的bi, 512 bit
        bitplanes = BitStream().join(bitplanes)  # 把列表拼接成二进制对象
        bitstream.append(bitplanes)
    bitstream = BitStream().join(bitstream)  # 把列表拼接成二进制对象
    return bitstream

# TODO
def to_blocks(img: Image.Image) -> List[Image.Image]:
    """把Image对象拆分成K=MN/64个64个像素的块Oi，并作为列表返回"""
    # 使用Image的crop方法
    pass

def to_bitplanes(block: Image.Image) -> List[BitStream]:
    """把块Oi (64个像素) 转换成向量组bi (64bit*8=512bit)。bi的每个元素是bi^(k), 64bit"""

    # 把每个像素点转换成二进制
    px = block.load()
    pixels = []  # type: List[BitStream] # 共64个像素点
    for y in range(block.height):
        for x in range(block.width):
            # x=0~width, y=0~height
            pixel = px[x,y]
            pixels.append(BitStream(uint=pixel, length=8))  # 8位无符号整数

    # 生成bitplanes，即论文中的向量组bi，64bit * 8 = 512 bit
    bitplanes = []
    for k in range(-1, -8-1, -1):
        # 把每个像素点的第k位取出来组成一个bitplane，即论文中的bi^(k)，64 bit
        bitplane = BitStream()
        for pixel in pixels: # 64个像素
            bitplane += BitStream(bool=pixel[k])  # k=-1即第0位(最低位)，-2即第1位，以此类推
        bitplanes.append(bitplane)

    return bitplanes

# TODO
def segment(bitstream: BitStream) -> List[bytes]:
    """把b分成4K个段，每个段即si^(j)是一个128 bit=16 byte字节流，返回所有段构成的数组，用于输入加密器"""
    pass

# TODO
def divide(seg: List[bytes]) -> BitStream:
    """把加密后的段e分解成密文字节流c，即segment函数的逆过程，用于输入解密器（或嵌入信息）"""
    pass

# TODO
def bitstream_to_img(bitstream: BitStream) -> Image.Image:
    """输入密文字节流c，计算对应像素值，重构图片，即img_to_bitstream的逆过程，因此需要反向实现其中的各个函数。"""
    pass


if __name__ == '__main__':
    # 测试用
    block = Image.open(PIC_8_PATH)
    bitstream = []  # 所有分块转换得到的比特流，即论文中的b, 512*K bit
    bitplanes = to_bitplanes(block)  # 把一个块转换成bitplanes，即论文中的bi, 512 bit
    bitplanes = BitStream().join(bitplanes)  # 从列表转换成二进制对象
    bitstream.append(bitplanes)
    block = Image.open(PIC_8_2_PATH)
    bitplanes = to_bitplanes(block)  # 把一个块转换成bitplanes，即论文中的bi, 512 bit
    bitplanes = BitStream().join(bitplanes)  # 从列表转换成二进制对象
    bitstream.append(bitplanes)
    bitstream = BitStream().join(bitstream)  # 从列表转换成二进制对象
    print(bitstream)