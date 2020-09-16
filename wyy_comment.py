# -*- coding: utf-8 -*-
import collections
import datetime
import requests, execjs, json
import time
import wordcloud
import jieba
import PIL.Image as image
import numpy as np
import matplotlib.pyplot as plt  # 图像展示库


def get_comments(song_id):  # 获取 2020-09-16 --- 2020-08-27的评论信息
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36',
        'accept': '*/*',
    }

    with open('code.js', encoding='utf8') as f1:
        js = f1.read()
    js_tool = execjs.compile(js) #加密函数，上一篇里有提到

    now_day = datetime.date.today() #当天日期
    flag_info = None #重复评论标志
    num = 0
    for i in range(20, -1, -1):  # 获取 2020-08-27---2020-09-16 的日期
        pre_day = str(now_day - datetime.timedelta(days=i)) + ' 23:59:59'  # 获取T+1日期
        # 先转换为时间数组
        timeArray = time.strptime(pre_day, "%Y-%m-%d %H:%M:%S")
        # 转换为时间戳
        cursor = str(int(time.mktime(timeArray))) + '000'  # 拼接成13位时间戳
        print(pre_day, cursor)
        # 评论接口参数
        param = {"rid": "R_SO_4_" + song_id, "threadId": "R_SO_4_" + song_id, "pageNo": "1", "pageSize": "1000",
                 "cursor": cursor, "offset": "0", "orderType": "1", "csrf_token": "ff57cff46ebe79b9a51dd10f8c9181bb"}
        pdata = js_tool.call('d', str(param))
        response = requests.post('https://music.163.com/weapi/comment/resource/comments/get', headers=headers,data=pdata)
        # 获取评论信息
        data = json.loads(response.text)['data']
        comments = data.get('comments')
        # 存储评论信息
        with open('comments.txt', 'a', encoding='utf8') as f:
            for comment in comments:
                info = comment.get('content')
                if flag_info == info:  # 取到重复的评论则跳出循环，防止重复获取
                    break
                print(info)
                f.write(info + '\n')
                # folow_comments = comment.get('beReplied') # 附加的评论，暂不获取
                # if folow_comments:
                #     for folow_comment in folow_comments:
                #         print(folow_comment.get('content'))
                num += 1  # 获取评论数+1
        flag_info = comments[0]['content']  # 取每次请求的第一条
        print('每次请求的第一条', flag_info, '\n')
    print('获取评论数：', num)


# 分词
def fc_CN(text):
    # 接收分词的字符串
    word_list = jieba.cut(text)
    # 分词后在单独个体之间加上空格
    result = " ".join(word_list)
    return result

# 输出云词
def word_cloud():
    with open("./comments.txt", encoding='utf8') as fp:
        text = fp.read()
        # 将读取的中文文档进行分词
        text = fc_CN(text).replace('\n', '').split(' ')
        # 过滤部分分词
        filter_str = ['的', '，', '了', '我', '[', '你', '是', '就', ']', '！', '。', '？', '这', '不', '也', '都', '吧', '啊', '在',
                      '吗', '和', '吗', '听', '有', '说', '去', '好', '人', '给', '他', '…', '小', '来', '还', '没', '一', '']
        new_text = []
        for data in text:
            if data not in filter_str:
                new_text.append(data)
        print(new_text)
        # 词频统计
        word_counts = collections.Counter(new_text)  # 对分词做词频统计
        word_counts_top10 = word_counts.most_common(10)  # 获取前10最高频的词
        print(word_counts_top10)  # 输出检查

        # 词频展示
        mask = np.array(image.open('./love.jpg'))  # 定义词频背景
        wc = wordcloud.WordCloud(
            # background_color='white',  # 设置背景颜色
            font_path='C:\Windows\Fonts\simhei.TTF',  # 设置字体格式
            mask=mask,  # 设置背景图
            max_words=200,  # 最多显示词数
            max_font_size=300,  # 字体最大值
            # scale=32  # 调整图片清晰度，值越大越清楚
        )

        wc.generate_from_frequencies(word_counts)  # 从字典生成词云
        image_colors = wordcloud.ImageColorGenerator(mask)  # 从背景图建立颜色方案
        wc.recolor(color_func=image_colors)  # 将词云颜色设置为背景图方案
        wc.to_file("./temp.jpg")  # 将图片输出为文件
        plt.imshow(wc)  # 显示词云
        plt.axis('off')  # 关闭坐标轴
        plt.show()  # 显示图像


if __name__ == '__main__':
    # 歌曲id
    song_id = '1474342935'
    get_comments(song_id)
    word_cloud()
