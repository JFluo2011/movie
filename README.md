# movie
flask python 微电影
根据微电影项目，练习flask，并进行代码重构。

TODO:
使用下面方式，重构模型，使得即便是查询所得的数据对象也会调用__init__方法，从而将可以初始化需要的数据
@orm.reconstructor
    def __init__(self):
        pass
