# -*- mode: python -*-
#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
sys.setrecursionlimit(5000)


def f_valid_url(target):
    import requests
    from validator_collection import validators, checkers
    if checkers.is_url(target):
        request = requests.get(target)
        if request.status_code == 200:
            return 1
        else:
            return 0
    else:
        return 0

def f_next_page(target, mainpage, pagenum):
    from bs4 import BeautifulSoup
    import requests
    req = requests.get(url=target)
    html = req.text
    bf = BeautifulSoup(html, 'html.parser')
    alllink = bf.find_all('a')
    p2links = BeautifulSoup(str(alllink), 'html.parser')
    linktemp = p2links.find_all('a')
    nextpage = '/'

    for each in linktemp:
        linkstr = each.get('href')
        if pagenum == 1:  # 第一页
            if 'page=2' in linkstr:
                nextpage = mainpage + linkstr
        else:  # 其他页
            nextpagenum = pagenum + 1
            nextpagestr = 'page=' + str(nextpagenum)
            if nextpagestr in linkstr:
                nextpage = mainpage + linkstr

    if nextpage == '/' or f_valid_url(nextpage) == 0:
        return 0
    else:
        return nextpage

def f_content_link(target, mainpage):
    from bs4 import BeautifulSoup
    import requests

    req = requests.get(url=target)
    html = req.text
    bf = BeautifulSoup(html, 'html.parser')
    alllink = bf.find_all('a')
    p2links = BeautifulSoup(str(alllink),'html.parser')
    linktemp = p2links.find_all('a')
    linklist = ['' for n in range(1, 500)]  # 生成空list并修改list内容，比向list或set内添加内容速度快
    poststr = mainpage + 'post/'

    i = 0

    for each in linktemp:
        linkstr = each.get('href')
        if poststr in linkstr:
            if linkstr not in linklist:
                if f_valid_url(linkstr):
                    linklist[i] = linkstr
                    i = i + 1

    while '' in linklist:
        linklist.remove('')  # 删除掉多余的空值

    return linklist


# 标题信息
def f_title_info(target):

    from pathvalidate import sanitize_filename
    from bs4 import BeautifulSoup
    import requests

    req = requests.get(url=target)
    html = req.text
    bf = BeautifulSoup(html, 'html.parser')
    infotexts = bf.find_all('title')
    paragraphs = []

    for x in infotexts:
        paragraphs.append(str(x))

    titleinfo = paragraphs[0].replace('<title>', '')
    titleinfo = titleinfo.replace('</title>', '')
    titlestr = sanitize_filename(titleinfo)

    if titlestr == '':
        titlestr = '未命名'
    return titlestr

# 下载页面内容
def f_download(target, dpath):
    import html2text
    from pathvalidate import sanitize_filename
    from bs4 import BeautifulSoup
    import requests

    req = requests.get(url=target)
    html = req.text
    text_maker = html2text.HTML2Text()
    text_maker.ignore_images = True
    text_maker.ignore_links = True
    text_maker.bypass_tables = False
    text = text_maker.handle(html)

    titlestr = f_title_info(target)
    outputname = titlestr + '.txt'

    outputloc = dpath + '\\' + outputname
    with open(outputloc, 'w', encoding='utf-8') as f:  # windows txt uses gbk
        f.write('禁止商用\n')
        f.write('Copyright@' + target + '\n')
        f.write(text)  # write need to be str type. Int or list type is not valid
        f.close()


import os

lofterweb = input('请输入Lofter主页地址:\n')
dpath = input(r'请输入希望用于下载的文件夹路径:')

autocheck = 'yes'

if 'https' not in lofterweb:
    lofterweb = lofterweb.replace('http', 'https')

if 'lofter' not in lofterweb:
    autocheck = 'no'
    print('输入的不是lofter网址！')

lofterweb=lofterweb.replace(' ','')


if not f_valid_url:
    autocheck = 'no'
    print('输入的网址不存在！')


if not os.path.isdir(dpath):

    print('该文件夹不存在\n')
    autocheck = 'no'

    dpathcheck = input('输入yes:新建文件夹用于下载；输入其他内容：结束\n')
    if dpathcheck == 'yes':
        os.mkdir(dpath)

print('希望备份的Lofter主页：' + lofterweb + '\n')
print('下载路径：' + dpath + '\n')
dcheck = input('输入yes:确认进行下载；输入其他内容：结束\n')

if dcheck == 'yes' and autocheck == 'yes':

    pagecount = 1
    durl=lofterweb
    while pagecount <= 1000:  # 防止死循环
        if pagecount == 1:
            durl = lofterweb

        print('正在下载' + '第' + str(pagecount) + '页...\n')
        linklist = f_content_link(durl, lofterweb)

        for linki in linklist:
            f_download(linki, dpath)

        print('第' + str(pagecount) + '页下载完成\n')

        if not f_next_page(durl, lofterweb, pagecount) == 0:
            durl = f_next_page(durl, lofterweb, pagecount)
        else:
            break  # 找不到下一页，跳出循环

        pagecount = pagecount + 1

    print('下载完成')

else:
    print('请重新输入')
