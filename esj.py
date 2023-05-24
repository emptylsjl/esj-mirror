import os
import sys
import time
import requests
from bs4 import BeautifulSoup
import epub

chrome_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}


def link_html_get(target_url):
    try:
        web_request = requests.get(target_url, headers=chrome_header, timeout=60)
        return web_request.text
    except:
        print(target_url)
        print(sys.exc_info()[1])


def esj_get(c_dict, html, path):
    e_soup = BeautifulSoup(html, "html.parser")
    try:
        book_title = str(e_soup.h2.contents[0])
        book_title = book_title.translate(book_title.maketrans(" ", '_'))
        c_dict['content_info']['title'] = book_title
        c_dict['content_info']['author'] = e_soup.select('.list-unstyled')[0].contents[3].contents[2].text
        c_dict['content_info']['genre'] = str(e_soup.find(class_='list-unstyled').contents[1].contents[1])
    except: print(sys.exc_info()[1])
    try:
        c_dict['content_info']['raw_url'] = e_soup.select('.list-unstyled')[0].contents[9].contents[2].text
    except: print(sys.exc_info()[1])

    try:
        os.mkdir(path + book_title)
    except:
        print(sys.exc_info()[1])
    try:
        main_intro = e_soup.select(".description")[0].contents
        for i in range(len(main_intro)):
            main_intro[i] = main_intro[i].text
        c_dict['content_info']['intro'] = main_intro
    except:
        print(sys.exc_info()[1])
    chap_contents_html_list = e_soup.select("#chapterList > a")
    chap_link_list = []
    main_chap_list = []
    for i in chap_contents_html_list:
        if 'esj' in i.attrs["href"]:
            chap_link_list.append(i.attrs["href"])
            main_chap_list.append([i.text])
        else:
            c_dict['content_info']['out_esj'].append(i.attrs["href"])
            print('此章节不在esj域内 : ', i.attrs["href"])
    img_cover_link = e_soup.select(".product-gallery > a > img")[0].attrs['src']
    img_cover_byte = requests.get(img_cover_link).content
    try:
        img_index = 1
        for esj_img_info in e_soup.select('.fr-fic'):
            esj_img_link = esj_img_info.attrs['src']
            esj_img_byte = requests.get(esj_img_link, headers=chrome_header, timeout=5).content
            c_dict['content_info']['esj_img'].append(
                ["esj_main_img" + str(img_index) + '.jpg', 'jpeg', esj_img_link, esj_img_byte])
            img_index += 1
    except:
        print(sys.exc_info()[1])
    img_index = 1
    index = 0
    main_contents_img_link = []
    for i in chap_link_list:
        print(i, end=" - ")
        c_html = link_html_get(i)
        c_soup = BeautifulSoup(c_html, "html.parser")
        main_contents_html = c_soup.select(".forum-content > p")
        main_contents_chap_text = []
        img_in_chunk_index = 0
        for j in main_contents_html:
            try:
                if len(j.text) > 100:
                    for line_text in j.text.split('\n'):
                        main_contents_chap_text.append(["text", line_text])
                    img_in_chunk = c_soup.find(class_="forum-content").find_all("img")
                    for i in img_in_chunk:
                        if img_in_chunk_index > 0:
                            break
                        img_link = i.attrs['src']
                        img_content_byte = requests.get(img_link, headers=chrome_header, timeout=10).content
                        main_contents_img_link.append(["main_content_img" + str(img_index), img_link, img_content_byte])
                        main_contents_chap_text.append(["main_content_img" + str(img_index), img_link])
                        img_in_chunk_index += 1
                        img_index += 1
                elif '「' in j.text or '」' in j.text or '[' in j.text or ']' in j.text:
                    main_contents_chap_text.append(["msg", j.text])
                elif j.text != "":
                    main_contents_chap_text.append(["text", j.text])
                elif 'src' in j.next.attrs:
                    img_link = j.next.attrs['src']
                    img_content_byte = requests.get(img_link, headers=chrome_header, timeout=10).content
                    main_contents_img_link.append(["main_content_img" + str(img_index), img_link, img_content_byte])
                    main_contents_chap_text.append(["main_content_img" + str(img_index), img_link])
                    img_index += 1
                else:
                    raise Exception
            except:
                try:
                    main_contents_chap_text.append(["unknown", j.text])
                except:
                    print(i)
                    print(sys.exc_info()[1])
        main_chap_list[index].append(main_contents_chap_text)
        index += 1
        try:
            print(index, " - ", main_chap_list[index-1][0])
        except:
            print(sys.exc_info()[1])
            print(main_contents_chap_text)

    c_dict["content_image"] = [["cover.jpg", "jpeg", img_cover_link, img_cover_byte]]
    for i in main_contents_img_link:
        c_dict["content_image"].append([i[0] + ".jpg", "jpeg", i[1], i[2]])
    index = 1
    c_dict["content_main"]["cover"] = ["cover", ["cover&info", "cover_img", c_dict["content_info"]]]
    for i in main_chap_list:
        c_dict["content_main"]["content_" + str(index)] = i
        index += 1
    for i in c_dict["content_main"].items():
        c_dict["content_toc"].append([i[0], i[1][0], i[0] + '.xhtml'])
    txt_content = ""
    for i in c_dict["content_main"].values():
        txt_content += i[0] + "\n" + "\n" + "\n"
        if len(i) == 2:
            main_txt = i[1]
            for j in main_txt:
                if type(j) == tuple:
                    txt_content += j[1] + '\n'
            txt_content += "\n" + "\n" + "\n"
    c_dict["content_txt"] = txt_content

    return c_dict


def build(url):
    try:
        s_t = time.time()

        c_dict = {}
        c_dict["content_info"] = {}
        c_dict["content_font"] = []
        c_dict["content_image"] = []
        c_dict["content_toc"] = []
        c_dict["content_txt"] = ''
        c_dict["content_main"] = {}
        c_dict['content_info']['title'] = '...'
        c_dict['content_info']['illus'] = '...'
        c_dict['content_info']['author'] = '...'
        c_dict['content_info']['trans'] = '...'
        c_dict['content_info']['genre'] = '...'
        c_dict['content_info']['condition'] = '...'
        c_dict['content_info']['intro'] = []
        c_dict['content_info']['esj_img'] = []
        c_dict['content_info']['out_esj'] = []
        c_dict['content_info']['raw_url'] = ''
        c_dict['content_info']['compare'] = []
        c_dict['content_info']['word_count'] = ''
        c_dict['content_info']['publisher'] = '...'
        c_dict['content_info']['source'] = '...'
        c_dict['content_info']['language'] = 'zh_CN'
        path = input("write to : ")
        html = link_html_get(url)
        if "alert('此小說可能已被下架或刪除!')" in html:
            print("已被下架 - " + url)
            return
        c_dict = esj_get(c_dict, html, path)
        title = c_dict['content_info']['title']
        book_path = path + title + "/"
        epub.build(c_dict, book_path)
        print("esj域内总章节数 : ", len(c_dict["content_main"])-1)
        print("esj域外章节数 : ", len(c_dict['content_info']['out_esj']))
        print("complete")
        print("--- %s seconds ---" % (time.time() - s_t))

    except:
        print(sys.exc_info()[1])


while True:
    target_url = input("esj url : ")
    if target_url == 'exit':
        print("abort")
        break
    build(target_url)
