# RDH-EI_cqu
专业综合设计

# 环境配置
> 本项目使用虚拟环境，安装在venv目录下，方便所有人同步需要的第三方库，而且不污染本地python环境，不使用时直接删除venv文件夹即可完全删除。
1. 运行`生成虚拟环境.bat`
2. 运行`安装依赖包.bat`
    
    > 目前主要安装 Pillow (图片处理)、Crypto (加解密，windows中为pycryptodome)、PyQt5 (GUI)，需要新的包通知我，会再更新。
3. 在IDE（如Pycharm）中配置python解释器为`venv\Scripts\python.exe`
4. 如需在命令行中使用，运行根目录下的`activate.bat`，或输入`venv\Scripts\activate.bat`

# 任务

## 第一阶段

软件设计方案、程序流程框图。

框架搭建。

## 第二阶段 代码编写

1. 加密、解密算法。AES、CBC
2. 嵌入信息、提取信息算法。
2. 同时提取信息加解密。
3. GUI

## 第三阶段

课程设计报告

## 算法改进

彩色图片


# 评分标准
- 基本功能
- 平台技术。bitstring库的BitStream类处理二进制流。
- 算法改进。
  - [ ] 图片编码使用pillow遍历像素效率太低，转为numpy数组再进行处理。
  - [ ] GUI一次处理多张图片。
  - [ ] 实现对彩色图片的处理
  - [x] 根据数据量大小和密文流自动确定合适的参数。
  - [x] 论文有误，嵌入、提取信息时LSB不需要打乱。打乱反而让图像质量变差了。
- 软件易用性

参考文献：

Qian Z, Zhang X, Ren Y, et al. Block cipher based separable reversible data hiding in encrypted images[J]. Multimedia Tools and Applications, 2016, 75(21): 13749–13763.

