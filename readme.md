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
- 一个id对应的文件包含6.6k篇文档，一篇文档需要进行三次渲染，大概需要6h，具体用时视网速而定.
- An id file contains 6.6k documents, and a document needs to be rendered three times. It takes about 8 hours, depending on the speed of the network.

# pool
40~179

# data path
* 0~3, mbp
* 4~9, thinkpad
* 10~14, mbp
* 15~19, x1 carbon
* 20~29, 185
* 30~39, mbp
* 180~182, thanks to ws
* 183~184, thanks to mxy
* 185, mbp
* 190~199, pc