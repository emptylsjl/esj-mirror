import os
import json
import random
import shutil
import sys
import time
import requests
from datetime import datetime

title = '...'
illus = '...'
author = '...'
source = 'internet'
subject = 'light_novel'
language = 'zh-CN'
publishers = 'sjl_lls'
cover_image = 'cover.jpg'
source_right = '' + author
date_creation = datetime.now()
content_version = ['Version.#', 'Version.Name']
date_modification = date_creation


def epub_var_global(content_name_dict: dict):
    global title, illus, author, publishers, language, source, subject
    try:
        title = content_name_dict['content_info']['title']
        illus = content_name_dict['content_info']['illus']
        author = content_name_dict['content_info']['author']
        source = content_name_dict['content_info']['source']
        language = content_name_dict['content_info']['language']
    except:
        print("info error")


def file_write(path, content, mode="w", use_encoding='utf-8'):
    try:
        with open(path, mode, encoding=use_encoding) as fw:
            fw.write(content)
    except:
        print(sys.exc_info()[1])


def epub_img_write(file_path: str, content_name_dict: dict):
    for i in content_name_dict["content_image"]:
        file_write(file_path + i[0], bytes(i[3]), mode="wb", use_encoding=None)
    for i in content_name_dict["content_info"]["esj_img"]:
        file_write(file_path + i[0], i[3], mode="wb", use_encoding=None)


def epub_container() -> str:
    container_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n    <rootfiles>\n        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n   </rootfiles>\n</container>'
    return container_xml


def epub_minetype() -> str:
    return "application/epub+zip"


def epub_opf_metadata() -> str:
    metadata = '    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">\n        <dc:identifier id="BookId" opf:scheme="UUID">urn:uuid:A1A2A3A4-A5A6A7A8-ASDHSA-D74ADHUI</dc:identifier>\n        <dc:creator opf:file-as="kid" opf:role="aut">' + author + '</dc:creator>\n        <dc:title>' + title + '</dc:title>\n        <dc:subject>' + subject + '</dc:subject>\n        <dc:rights>' + source_right + '</dc:rights>\n        <dc:language>' + language + '</dc:language>\n        <dc:publisher>emptylls_sjl</dc:publisher>\n        <dc:date>' + date_creation.__str__() + '</dc:date>\n        <dc:source>sjl_lls</dc:source>\n        <dc:date opf:event="modification">' + date_modification.__str__() + '</dc:date>\n        <meta name="cover" content="' + cover_image + '" />\n        <meta property="dcterms:rights">' + source_right + '</meta>\n        <meta property="dcterms:publisher">' + publishers + '</meta>\n        <meta id="meta-title" property="dcterms:title">' + title + '</meta>\n        <meta property="dcterms:date">' + date_creation.__str__() + '</meta>\n        <meta property="dcterms:modified">' + date_modification.__str__() + '</meta>\n        <meta id="meta-language" property="dcterms:language">' + language + '</meta>\n        <meta content="' + content_version[0] + '" name="' + content_version[1] + '" />\n    </metadata>"\n'
    return metadata


def epub_opf_manifest(content_name_dict: dict) -> str:
    content = '        <item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml" />\n        <item href="toc.xhtml" id="toc" media-type="application/xhtml+xml" properties="nav">\n        <item href="Styles/style.css" id="style.css" media-type="text/css" />\n        <item href="Misc/notereplace.js" id="notereplace.js" media-type="text/plain" />\n'
    font_ttf = ''
    if "content_font" in content_name_dict:
        for font_name in content_name_dict['content_font']:
            font_ttf += '        <item href="Fonts/' + font_name + '" id="' + font_name + '" media-type="application/x-font-ttf" />\n'
    esj_image = ''
    for esj_img in content_name_dict['content_info']['esj_img']:
        esj_image += '        <item href="Images/' + esj_img[0] + '" id="' + esj_img[0] + '" media-type="image/' + esj_img[1] + '" />\n'
    content_image = ''
    if "content_image" in content_name_dict:
        for content_img in content_name_dict["content_image"]:
            content_image += '        <item href="Images/' + content_img[0] + '" id="' + content_img[0] + '" media-type="image/' + content_img[1] + '" />\n'
    content_text = ''
    if "content_main" in content_name_dict:
        for content_main in content_name_dict["content_main"]:
            content_text += '        <item href="Text/' + content_main + '.xhtml" id="' + content_main + '.xhtml" media-type="application/xhtml+xml" />\n'
    manifest = \
        '    <manifest>\n' + \
        content + \
        font_ttf + \
        esj_image + \
        content_image + \
        content_text + \
        '    </manifest>\n'

    return manifest


def epub_opf_spine(content_name_dict: dict) -> str:

    item_id = ''
    if "content_toc" in content_name_dict:
        for item in content_name_dict["content_toc"]:
            item_id += '        <itemref idref="' + item[0] + '.xhtml"/>\n'

    spine = \
        '    <spine toc="ncx">\n' + \
        item_id + \
        '    </spine>\n'
    return spine


def epub_opf(content_name_dict: dict) -> str:

    guide = \
        '    <guide>\n' + \
        '        <reference href="toc.xhtml" title="Table of Contents" type="toc"></reference>\n' + \
        '    </guide>\n'

    opf = \
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + \
        '<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">\n' + \
        epub_opf_metadata() + \
        epub_opf_manifest(content_name_dict) + \
        epub_opf_spine(content_name_dict) + \
        guide + \
        '</package>'

    return opf


def epub_toc_head_doc() -> str:

    head = \
        '    <head>\n' + \
        '        <meta name="dtb:uid" content="urn:uuid:A1A2A3A4-A5A6A7A8-ASDHSA-D74ADHUI" />\n' + \
        '        <meta name="dtb:depth" content="1" />\n' + \
        '        <meta name="dtb:totalPageCount" content="0" />\n' + \
        '        <meta name="dtb:maxPageNumber" content="0" />\n' + \
        '    </head>\n'
    doc_title = \
        '    <docTitle>\n' + \
        '        <text>' + title + '</text>\n' + \
        '    </docTitle>\n'
    doc_author = \
        '    <docAuthor>\n' + \
        '        <text>' + author + '</text>\n' + \
        '    </docAuthor>\n'

    return head + doc_title + doc_author


def epub_toc_navmap(content_name_dict: dict) -> str:

    nav_point = ''
    if "content_toc" and "content_main" in content_name_dict:
        index = 1
        for nav_label_content in content_name_dict["content_toc"]:

            nav_point += \
                '    <navPoint id="' + nav_label_content[0] + '" playOrder="' + str(index) + '">\n' + \
                '        <navLabel>\n' + \
                '            <text>' + nav_label_content[1] + '</text>\n' + \
                '        </navLabel>\n' + \
                '        <content src="Text/' + nav_label_content[0] + '.xhtml" />\n' + \
                '    </navPoint>\n'

            index += 1

    nav_map = \
        '    <navMap>\n' + \
        nav_point + \
        '    </navMap>\n'

    return nav_map


def epub_toc(content_name_dict: dict) -> str:
    toc = \
        '<?xml version="1.0" encoding="utf-8"?>\n' + \
        '<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n' + \
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n' + \
        epub_toc_head_doc() + \
        epub_toc_navmap(content_name_dict) + \
        '</ncx>\n'

    return toc


def epub_chap_main_text(main_content_tuple: tuple, div_class: str) -> str:

    text = \
        '<?xml version="1.0" encoding="utf-8"?>\n' + \
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n' + \
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xmlns:xml="http://www.w3.org/XML/1998/namespace" xml:lang="zh-CN">\n' + \
        '<head>\n' + \
        '    <link href="../Styles/style.css" rel="stylesheet" type="Text/css"/>\n' + \
        '    <title>' + main_content_tuple[0] + '</title>\n' + \
        '</head>\n\n'

    text += \
        '<body>\n' + \
        '    <div class="' + div_class + '">\n' + \
        '        <p class="h2">' + main_content_tuple[1][0] + '</p>\n\n'

    index = 0
    for text_list in main_content_tuple[1][1]:
        if 'text' in text_list[0]:
            text += '        <p>' + text_list[1] + '</p>\n'
        elif 'msg' in text_list[0]:
            text += '        <p>' + text_list[1] + '</p>\n'
        elif 'img' in text_list[0]:
            text += \
                '        <div class="illus">\n' + \
                '            <img alt="' + text_list[0] +'" src="../Images/' + text_list[0] +'.jpg"/>\n' + \
                '        </div>\n'
        elif 'unknown' in text_list[0]:
            if index % 2 == 0:
                text += '        <p><br/></p>\n'
            index += 1

    text += \
        '    </div>\n' + \
        '</body>\n' + \
        '</html>'

    return text


def epub_content_cover(content_name_dict: dict) -> str:
    text = '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.lls.org/2007/ops" xmlns:xml="http://www.w3.org/XML/1998/namespace" xml:lang="zh-CN">\n<head>\n    <link href="../Styles/style.css" rel="stylesheet" type="Text/css"/>\n    <title>Cover</title>\n</head>\n\n<body>\n    <div style="text-align: center; padding: 0pt; margin: 0pt;">\n        <svg xmlns="http://www.w3.org/2000/svg" height="100%" preserveAspectRatio="xMidYMid meet" version="1.1" viewBox="0 0 1804 2560" width="100%" xmlns:xlink="http://www.w3.org/1999/xlink">\n            <image width="1804" height="2560" xlink:href="../Images/cover.jpg"/>\n        </svg>\n   </div>\n'
    try:
        text += '    <div class="title" style="margin: 5em 0em;">\n        <p class="h2" style="margin: 0;">' + content_name_dict['content_info']['title'] + '</p>\n        <p class="center" style="margin: 2em 0 0 0.3em; line-height: 1em;"><span class="em06">author／</span><span class="tbox">' + content_name_dict['content_info']['author'] + '</span></p>\n        <p class="center" style="margin: 2em 0 0 0.3em; line-height: 1em;"><span class="em06">illus／</span><span class="tbox">' + illus + '</span></p>\n        <p class="center" style="margin: 2em 0 0 0.3em; line-height: 1em;"><span class="em06">' + date_creation.__str__() + '</span></p>\n        <p class="center" style="margin: 2em 0 0 0.3em; line-height: 1em;"><span class="em06"><a href="' + content_name_dict['content_info']['raw_url'] + ">' + content_name_dict['content_info']['raw_url'] + '</a></span></p>\n    </div>\n'
        intro = ''
        for i in content_name_dict['content_info']['intro']:
            intro += '        <p class="intro">' + i + '</p>\n'
        text += '    <div>\n        <p class="h3">intro</p>\n        <p class="intro">──────────────</p>\n' + intro + '    </div>\n'
    except:
        print("info error")
    text += '    <div class="illus">\n'
    for i in content_name_dict['content_info']['esj_img']:
        text += '        <img src="../Images/' + i[0] + '"/>\n'
    text += '    </div>\n'

    content_text = ''
    for i in content_name_dict['content_main'].items():
        content_text += '        <p class="text1"><a href="../Text/' + i[0] + '.xhtml"><span class="co0">' + i[1][0] + '</span></a></p>\n'
    text += \
        '    <div class="em08 bold" style="margin: 3em 0em;">\n        <p class="h2"><b>CONTENTS</b></p>\n' + content_text + '    </div>\n</body>\n</html>'
    return text


def epub_content_main_str_iterate(content_name_dict: dict):
    # aaa = time.time()
    index = 0
    for i in content_name_dict['content_toc']:
        content_name_dict['content_toc'][index][1] = i[1].translate(i[1].maketrans("<>&", '〈〉/'))
        index += 1
    index = 0
    for chap_text in content_name_dict['content_main'].items():
        if chap_text[0] != 'cover':
            content_name_dict['content_main'][chap_text[0]][0] = chap_text[1][0].translate(chap_text[1][0].maketrans("<>&", '〈〉/'))
            chap_line_text = iter(chap_text[1][1])

            for index in range(len(content_name_dict['content_main'][chap_text[0]][1])):
                text = next(chap_line_text)[1]
                content_name_dict['content_main'][chap_text[0]][1][index][1] = text.translate(text.maketrans("<>&", '〈〉/'))
    # print("\n---- %s seconds ----\n" % (time.time() - aaa))
        # index += 1


def epub_create(content_name_dict: dict, path):

    os.mkdir(path + "epub")
    os.mkdir(path + "epub/OEBPS")
    os.mkdir(path + "epub/META-INF")
    os.mkdir(path + "epub/OEBPS/Text")
    os.mkdir(path + "epub/OEBPS/Images")
    os.mkdir(path + "epub/OEBPS/Styles")
    file_write(path + "epub/mimetype", epub_minetype())
    file_write(path + "epub/META-INF/container.xml", epub_container())
    file_write(path + "epub/OEBPS/content.opf", epub_opf(content_name_dict))
    file_write(path + "epub/OEBPS/toc.ncx", epub_toc(content_name_dict))
    css = ".body{`	padding: 0%;`	margin-top: 0%;`	margin-bottom: 0%;`	margin-left: 1%;`	margin-right: 1%;`	line-height: 130%;`	text-align: justify;`}`.h1{`	font-size: 1.8em;`	line-height: 120%;`	text-align: center;`	font-weight: bold;`	margin-top: 0.1em;`	margin-bottom: 0.4em;`}`.h2{`	font-size: 1.5em;`	line-height: 120%;`	text-align: center;`	font-weight: bold;`	margin-top: 0.3em;`	margin-bottom: 0.5em;`}`.h3{`	font-size: 1.4em;`	line-height: 120%;`	text-indent: 0em;`	font-weight: bold;`	margin-top: 0.5em;`	margin-bottom: 0.2em;`}`.div{`	margin: 0px;`	padding: 0px;`	text-align: justify;`}`.p{`	text-indent: 2em;`	display: block;`	line-height: 1.3em;`	margin-top: 0.4em;`	margin-bottom: 0.4em;`}`.illus{`	text-indent: 0em;`	text-align: center;`}`.cover{`	margin: 0em;`	padding: 0em;`	text-indent: 0em;`	text-align: center;`}`.right{`	text-indent: 0em;`	text-align: right;`}`.left{`	text-indent: 0em;`	text-align: left;`}`.center{`	text-indent: 0em;`    text-align: center;`}`.bold{`    font-weight: bold;`}`.intro{`    font-size: 0.8em;`	text-indent: 0em;`	line-height: 1.0em;`	margin-top: 0.2em;`	margin-bottom: 0.2em;`}`.em06{`    font-size: 0.6em;`}`.em08{`    font-size: 0.8em;`}`.em12{`    font-size: 1.2em;`}`.em14{`    font-size: 1.4em;`}`.em16{`    font-size: 1.6em;`}`.em18{`    font-size: 1.8em;`}`.em20{`    font-size: 2em;`}`/* @font-face{`    font-family: "title";`    src: url(../Fonts/title.ttf);`}`.title{`    font-family: title;`} */`.chap{`    font-size: 0.8em;`	margin: 1em 0 -0.8em 0em;`}`.text1{`	text-indent: 0em;`	text-align: left;`	text-decoration: none;`    margin: 0.9em -0.8;``}`.co0{`	color: rgb(121, 124, 106);`}`.co1{`	color: #7B6CB1;`}`.co2{`	color: #7ECDF4;`}`.co3{`	color: #FFF;`}`"
    css.translate(css.maketrans("`", "\n"))
    file_write(path + "epub/OEBPS/Styles/style.css", css)
    for i in content_name_dict["content_main"].items():
        if i[0] == "cover":
            file_write(path + "epub/OEBPS/Text/" + i[0] + ".xhtml", epub_content_cover(content_name_dict))
        else:
            file_write(path + "epub/OEBPS/Text/" + i[0] + ".xhtml", epub_chap_main_text(i, "chap"))
    epub_img_write(path + "epub/OEBPS/Images/", content_name_dict)

    
def epub_7z(path, des_path, b_title):
    archive_text = ""
    archive_text += '' + path + 'epub/META-INF\n'
    archive_text += '' + path + 'epub/OEBPS\n'
    archive_text += '' + path + 'epub/mimetype'
    file_write(path + "/7z_list.txt", archive_text)
    os_input = '7z a -tzip "' + des_path + "/" + b_title + '.epub" @' + path + "/" + '7z_list.txt'
    os.system(os_input)

# def build():
def build(c_dict, book_path):
    try:
        s_t = time.time()
        title = c_dict['content_info']['title']
        try:
            shutil.rmtree(book_path + "epub")
        except:
            print(sys.exc_info()[1])

        epub_content_main_str_iterate(c_dict)
        epub_var_global(c_dict)
        epub_create(c_dict, book_path)

        # try:
        #     des_path = path
        #     epub_7z(path, des_path, title)
        # except:
        #     print(sys.exc_info()[1])

        print("--- %s seconds ---" % (time.time() - s_t))

    except:
        print(sys.exc_info()[1])
