# 感谢你的帮助！！！
# Thanks for your help!!!

# 步骤 steps
首先请确保可以访问[Quora](https://www.quora.com/). 

Please make sure you can connect to [Quora](https://www.quora.com/).

在命令行运行下列指令.

Run the following scripts. 
```
git clone https://github.com/ZizhenWang/QuoraCrawler.git
cd QuoraCrawler/
pip install -r requirements.txt
```
从[官网](https://selenium-python.readthedocs.io/installation.html)下载与浏览器对应版本的selenium,并添加至系统路径.
 
Download selenium from [website](https://selenium-python.readthedocs.io/installation.html) and add it to system PATH.

从[可选id](#pool)中选择一个或多个id

Select one or more ids from available id [pool](#pool).

对于一个id，如`0`，请运行

For single id as `0`, please run

```
python crawl.py -i 0
```

对于多个id，如`0,1,2,3,4`，请运行

For single id as `0,1,2,3,4`, please run

```
python crawl.py -i 0,1,2,3,4
```

# 注意 Notes
- python版本为3.6
- python version is 3.6
- 如果你准备或已经运行了部分数据的爬虫，请将对应的id邮件告知我或通过issue提交，避免重复采集，再次感谢你的帮助！
- If you are ready to run some ids' crawler, please informs me by email or issue to avoid duplicate crawling, thanks for your help again! 
- 一个id对应的文件包含6k篇文档，一篇文档需要进行三次渲染，大概需要6h，具体用时视网速而定.
- An id file contains 6.6k documents, and a document needs to be rendered three times. It takes about 8 hours, depending on the speed of the network.

# pool
0~89

# data path
|range|path|state|
|:---:|:---:|:---:|
|0,1|local|
|2~9|tp|
|10~19|yl||
|20~29|lili|
|30~39|vm|
|50~59|wlh|
|60~64|local|

# ** 06.27 updates
1. 更新了待爬取的问题表
2. 更新了部分爬取代码

# deprecated records
|range|path|state|
|:---:|:---:|:---:|
|0,3|mbp|done|
|4,9|carbon|in progress|
|10,14|mbp|done|
|15,19|carbon|in progress|
|20,29|185|in progress|
|30,39|mbp|in progress|
|81|-------|***train/test boundary***|
|185|mbp|in progress|
|190,199|pc|in progress|