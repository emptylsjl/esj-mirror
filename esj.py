
import base64
import dataclasses
import hashlib
import json
import os
import sys
import time
import logging
import traceback
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import bs4
import requests
from bs4 import BeautifulSoup

import r
import epub
from r import gv

no_cover_b64 = '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'

r.set_logger('epub.log')
loggerA = r.get_logger('esj_c')

cookie = r.make_cookie(
    "copy paste the cookie from browser to here",
    'esjzone.cc'
)

def parse_chap(sp: bs4.BeautifulSoup, format_=0) -> list:
    chap_list = sp.find(id="chapterList")

    tags = chap_list.select('summary, a, p.non')
    chaps = [['part_0', [], []]]
    for i in tags:
        if i.name in ["p", 'summary'] and i.text.strip():
            if chaps[-1][2]:
                chaps.append([f'part_{len(chaps)}', [i.text], []])
            else:
                chaps[-1][1].append(i.text)

        elif i.name == 'a' and "esjzone.cc" in i.attrs['href']:
            chaps[-1][-1].append([f'{chaps[-1][0]}_chap_{len(chaps[-1][-1])}', i.text, i.attrs['href'], [], []])

    return chaps


def parse_info(sp: bs4.BeautifulSoup, url: str):
    try:
        loggerA.info(f'parse info - {url}')
        header = sp.find(class_='book-detail')
        attrs = dict([i.text.split(':', 1) for i in header.ul.find_all("li") if ':' in i.text])

        return {
            'title': header.h2.text,
            'title_raw': attrs.get('其他書名'),
            'author': attrs.get('作者'),
            'author_raw': attrs.get('作者'),
            'cover_src': img['src'] if (img := sp.select_one(".product-gallery img")) else None,
            'illustrator': None,
            'translater': None,
            'type': attrs.get('類型'),
            'subject': 'light_novel',
            'tags': [i.text.strip() for i in sp.find().select(".m-t-20 > a") if i.text.strip()],
            'state': None,
            'intro': [i.text.strip() for i in sp.select(".description p") if i.text.strip()],
            'intro_html': str(sp.select(".description")),
            'esj_img_srcs': [],
            'chap_redirect': [[i.text, i['href']] for i in sp.select('#chapterList > a') if "esjzone.cc" not in i['href']],
            'publisher': 'kj',
            'temp_d': None,
            'source': 'network',
            'site': 'esj',
            'site_url': url,
            'name_hash': hashlib.sha256((url+header.h2.text).encode('utf-8')).hexdigest(),
            'source_site': attrs.get('Web生肉'),
            'language': 'zh_CN',
        }
    except Exception as e:
        loggerA.error(f'block parse: {traceback.format_exc()}')


def get_img_b64(s: requests.Session, img_url: str, img_id) -> list:
    loggerA.info(f'GET_img: {img_id} {img_url}')
    if r.validate_url(img_url):
        if (img_resp := s.get(img_url)).ok:
            return [img_resp.ok, img_resp.status_code, img_url, r.guess_img(img_resp.content), r.dump(img_resp.content, 'b64')]
        loggerA.error(f'GET_img fail:{img_resp.status_code} {img_id} {img_url}')
        return [img_resp.ok, img_resp.status_code, img_url, 'none', '']
    loggerA.error(f'GET_img fail:invalid url {img_id} {img_url}')


def iter_chaps(s: requests.Session, c_dict: dict, html_dir: Path):
    img_index = [1]
    for _, tags, section in c_dict['chaps']:
        for chap_id, title, url, header, content in section:
            loggerA.info(f'start chap - url:{url}, index:{chap_id}, title:{title}')

            if (html_path := (html_dir / f'{chap_id}.html')).exists():
                resp_html = r.rt(html_dir / f'{chap_id}.html')
                time.sleep(0.1)
            else:
                if not ((resp := s.get(url)).ok and (resp_html := resp.text)):
                    loggerA.error(f'GET_chap:{resp.status_code} {url:52} - {title}')
                    return
                wf = r.wt(html_dir/f'{chap_id}.html', resp_html)
                loggerA.info(f'file write:{str(wf)} saved - ({title})')
                time.sleep(2)

            sp = BeautifulSoup(resp_html, "html.parser")
            header += [i.text for i in sp.select(".single-post-meta > div")]
            main_content = sp.find(class_="forum-content")
            text_chunk = main_content.text

            def add_img(img_tag: bs4.Tag):
                img_id = f'img_{chap_id}_{img_index[0]}'
                if not (img_resp := get_img_b64(s, img_tag['src'], img_id)):
                    return
                content.append(["img", img_id] + img_resp[:-1])
                c_dict['imgs'].append(['chap_img', img_id] + img_resp)
                img_index[0] += 1

            for block in main_content.find_all('p'):
                try:
                    for line in [j for j in block.text.split('\n') if j.strip()]:
                        content.append(["text", line, ''])
                    for img in block.select('img[src]'):
                        add_img(img)
                except:
                    loggerA.error(f'block parse fail: {traceback.format_exc()}')
                    content.append(["error", block.text])

            imgs = main_content.find_all('img')
            if len(imgs) != len(p_img := [line[4] for line in content if line[0] == "img"]):
                try:
                    loggerA.warning(f'img not in p {url} - {title}')
                    for i in imgs:
                        if i['src'] not in p_img:
                            add_img(i)
                except:
                    loggerA.error(f'add missing img fail: {traceback.format_exc()}')


def add_cover(s: requests.Session, c_dict: dict):
    if (img_resp := get_img_b64(s, c_dict['info']['cover_src'], 'cover_0')) and img_resp[0]:
        c_dict['imgs'].append(['cover', 'cover_0'] + img_resp)
    else:
        c_dict['imgs'].append(['cover', 'cover_0', True, None, None, 'png', no_cover_b64])


def main(out_path: str, url: str, ignore_hash=False):
    try:
        url_hash = r.sha265(url)[:32]
        if (not ignore_hash) and (bk_path := next((i for i in Path(out_path).iterdir() if url_hash in i.name), None)) and (bk_path/'bk.json').exists():
            loggerA.info(f'fetch cache found: {url_hash}')
            c_dict_str = r.rt(bk_path / 'bk.json')

        else:
            session = requests.session()
            session.headers.update(gv.user_Agent)
            session.cookies.update(cookie)

            if not (resp := session.get(url)).ok:
                loggerA.error(f'GET_book:{resp.status_code} {url:52}')
                return

            soup = BeautifulSoup(resp.text, "html.parser")

            c_dict = {
                'info': parse_info(soup, url),
                'chaps': parse_chap(soup),
                'imgs': [],
                'fonts': [],
            }
            add_cover(session, c_dict)

            bk_html_dir = r.mkdir(f'{out_path}/{c_dict["info"]["title"]}_{url_hash}/html')
            r.wt(bk_html_dir/'chap.html', str(soup))
            iter_chaps(session, c_dict, bk_html_dir)
            loggerA.info(f'fetch end: {url}')

            bk_path = bk_html_dir.parent
            # r.wb('bk.pk', c_dict, 'pk')
            c_dict_str = r.dump(c_dict, 'json')
            r.wt(bk_path/'bk.json', c_dict_str)
            loggerA.info(f'fetch cached: {url}')

        loggerA.info(f'epub build start: {url_hash}')

        c_dict_str = r.str_trans(c_dict_str, '<>&', '⋖⋗·')
        epub.build(bk_path, json.loads(r.xml_repl('', c_dict_str)))

        loggerA.info(f'epub build end: {url_hash}')

    except:
        loggerA.error(f'fail ---- {traceback.format_exc()}')


url_1 = 'https://www.esjzone.cc/detail/1626494386.html'
url_3 = "https://www.esjzone.cc/detail/1611769112.html"
main('out', url_3)