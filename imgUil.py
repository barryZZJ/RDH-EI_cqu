from typing import List
from PIL import Image
from bitstring import BitStream
from consts import *

def img_to_bitstream(filepath: str) -> BitStream:
    """输入图片路径，返回编码后的字节流，即论文中的b"""
    img = Image.open(filepath)  # type: Image.Image  # 用PIL打开图片，得到Image对象
    blocks = _to_blocks(img)  # type: List[Image.Image]  # 分成K个8x8的块 (论文中Oi)
    list_of_bitplanes = []  # 所有位平面列表构成的列表 (论文中b), 512*K bit。一个位平面列表是论文中的bi, 64bit * 8 = 512 bit；一个位平面是论文中的bi^(k), 64 bit。
    for block in blocks:
        bitplanes = _block_to_bitplanes(block)  # 把一个块转换成位平面列表(论文中bi), 512 bit
        list_of_bitplanes.append(bitplanes)

    bitstream = join(list_of_bitplanes)  # 把列表合并成比特流
    return bitstream

# TODO
def _to_blocks(img: Image.Image) -> List[Image.Image]:
    """把图片拆分成K个块 (Oi, 64个像素)，并作为列表返回"""
    # 可使用Image.Image的crop方法
    pass

def _block_to_bitplanes(block: Image.Image) -> BitStream:
    """
    把一个块 (64个像素) 转换成位平面列表(论文中bi) (64bit*8=512bit)。
    一个位平面是论文中的bi^(k), 64 bit。
    """
    # 下划线表示是内部函数，其他文件其他模块不需要关心。
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

    bitplanes = join(bitplanes)  # 把列表合并成比特流
    return bitplanes

# TODO
def segment_every(bitstream: BitStream, bits: int) -> List[BitStream]:
    """
    比特流b，每bits个比特为一组，组成一个列表。
    如bits=128时，把bitstream分成128bit一组，每个元素即si^(j)就是一个128 bit的BitStream，用于输入加密器。
    bits=64u时，分组用于嵌入信息。

    注：加密器使用该输出时，可以通过列表里每个BitStream对象的bytes成员(如bitstream.bytes)把BitStream对象转换为字节。
    """
    pass

def join(seg: List[BitStream]) -> BitStream:
    """
    把列表的每个元素合并成一个完整的字节流

    注：输入字节密文列表时，要先把列表里每个密文字节转换成BitStream，可以通过BitStream(bytes=密文字节)实现
    """
    return BitStream().join(seg)

def bitstream_to_img(bitstream: BitStream) -> Image.Image:
    """输入密文字节流e，计算对应像素值，解码为图片，即img_to_bitstream的逆过程。"""
    list_of_bitplanes = segment_every(bitstream, 512)  # 分成K个512 bits的列表，每个元素是一个块的位平面列表
    blocks = []
    for bitplanes in list_of_bitplanes:
        block = _bitplanes_to_block(bitplanes)
        blocks.append(block)

    img = _from_blocks(blocks)
    #! 如果有需要可以添加保存到本地的函数
    return img

# TODO 待bitstream_to_img完善后实现。嵌入信息要用。为保留唯一性可以把bitstream_to_img的主要功能写在该函数里。
def bitstream_to_blocks(bitstream: BitStream) -> Image.Image:
    """输入密文字节流e，计算对应像素值，解码为各个图片块，不需要拼接"""
    pass

# TODO
def _bitplanes_to_block(bitplanes: BitStream) -> Image.Image:
    """把512bit的位平面列表bitplanes (论文中bi) 重构为一个块 (Oi, 64个像素)"""
    pass

# TODO
def _from_blocks(blocks: List[Image.Image]) -> Image.Image:
    """把图片分块合并成一个完整的图片，注意返回的是Image对象"""
    # 可使用Image.Image的paste方法
    pass

if __name__ == '__main__':
    # 测试用
    block = Image.open(PIC_8_PATH)
    list_of_bitplanes = []  # 所有位平面列表构成的列表 (论文中b), 512*K bit。一个位平面列表是论文中的bi, 64bit * 8 = 512 bit；一个位平面是论文中的bi^(k), 64 bit。
    bitplanes = _block_to_bitplanes(block)  # 把一个块转换成bitplanes，即论文中的bi, 512 bit
    list_of_bitplanes.append(bitplanes)
    block = Image.open(PIC_8_2_PATH)
    bitplanes = _block_to_bitplanes(block)  # 把一个块转换成位平面列表(论文中bi), 512 bit
    list_of_bitplanes.append(bitplanes)
    bitstream = join(list_of_bitplanes)  # 把列表合并成比特流
    print(bitstream)