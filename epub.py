
import os
import shutil
import traceback
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import r

css = '.body{\n\tpadding: 0%;\n\tmargin-top: 0%;\n\tmargin-bottom: 0%;\n\tmargin-left: 1%;\n\tmargin-right: 1%;\n\tline-height: 130%;\n\ttext-align: justify;\n}\n.h1{\n\tfont-size: 1.8em;\n\tline-height: 120%;\n\ttext-align: center;\n\tfont-weight: bold;\n\tmargin-top: 0.1em;\n\tmargin-bottom: 0.4em;\n}\n.h2{\n\tfont-size: 1.5em;\n\tline-height: 120%;\n\ttext-align: center;\n\tfont-weight: bold;\n\tmargin-top: 0.3em;\n\tmargin-bottom: 0.5em;\n}\n.h3{\n\tfont-size: 1.4em;\n\tline-height: 120%;\n\ttext-indent: 0em;\n\tfont-weight: bold;\n\tmargin-top: 0.5em;\n\tmargin-bottom: 0.2em;\n}\n.div{\n\tmargin: 0px;\n\tpadding: 0px;\n\ttext-align: justify;\n}\n.p{\n\ttext-indent: 2em;\n\tdisplay: block;\n\tline-height: 1.3em;\n\tmargin-top: 0.4em;\n\tmargin-bottom: 0.4em;\n}\n.illus{\n\ttext-indent: 0em;\n\ttext-align: center;\n}\n.cover{\n\tmargin: 0em;\n\tpadding: 0em;\n\ttext-indent: 0em;\n\ttext-align: center;\n}\n.right{\n\ttext-indent: 0em;\n\ttext-align: right;\n}\n.left{\n\ttext-indent: 0em;\n\ttext-align: left;\n}\n.center{\n\ttext-indent: 0em;\n    text-align: center;\n}\n.bold{\n    font-weight: bold;\n}\n.intro{\n    font-size: 0.8em;\n\ttext-indent: 0em;\n\tline-height: 1.0em;\n\tmargin-top: 0.2em;\n\tmargin-bottom: 0.2em;\n}\n.em06{\n    font-size: 0.6em;\n}\n.em08{\n    font-size: 0.8em;\n}\n.em12{\n    font-size: 1.2em;\n}\n.em14{\n    font-size: 1.4em;\n}\n.em16{\n    font-size: 1.6em;\n}\n.em18{\n    font-size: 1.8em;\n}\n.em20{\n    font-size: 2em;\n}\n/* @font-face{\n    font-family: "title";\n    src: url(../Fonts/title.ttf);\n}\n.title{\n    font-family: title;\n} */\n.chap{\n    font-size: 0.8em;\n\tmargin: 1em 0 -0.8em 0em;\n}\n.text1{\n\ttext-indent: 0em;\n\ttext-align: left;\n\ttext-decoration: none;\n    margin: 0.9em -0.8;\n\n}\n.co0{\n\tcolor: rgb(121, 124, 106);\n}\n.co1{\n\tcolor: #7B6CB1;\n}\n.co2{\n\tcolor: #7ECDF4;\n}\n.co3{\n\tcolor: #FFF;\n}\n'

loggerA = r.get_logger('esj_c')


def epub_container() -> str:
    container_xml = \
                    '<?xml version="1.0" encoding="UTF-8"?>\n' + \
                    '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n' + \
                    '    <rootfiles>\n' + \
                    '        <rootfile ' \
                    '            full-path="OEBPS/content.opf" \n' + \
                    '            media-type="application/oebps-package+xml"\n' + \
                    '        />\n' + \
                    '   </rootfiles>\n' + \
                    '</container>'
    return container_xml


def epub_mimetype() -> str:
    return "application/epub+zip"


def opf_metadata(c_dict: dict) -> str:
    info = c_dict['info']

    cover_image = 'cover_0.png'
    date_creation = datetime.now(timezone.utc)
    c_dict['info']['date_creation'] = date_creation

    metadata = \
        '    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">\n' + \
        '        <dc:identifier id="BookId" opf:scheme="UUID">urn:uuid:' + info['temp_d'] + '</dc:identifier>\n' + \
        '        <dc:creator opf:file-as="kid" opf:role="aut">' + info['author'] + '</dc:creator>\n' + \
        '        <dc:title>' + info['title'] + '</dc:title>\n' + \
        '        <dc:source>' + info['source'] + '</dc:source>\n' + \
        '        <dc:subject>' + info['subject'] + '</dc:subject>\n' + \
        '        <dc:language>' + info['language'] + '</dc:language>\n' + \
        '        <dc:publisher>' + info['publisher'] + '</dc:publisher>\n' + \
        '        <dc:date>' + date_creation.isoformat() + '</dc:date>\n' + \
        '        <dc:date opf:event="modification">' + date_creation.isoformat() + '</dc:date>\n' + \
 \
        '        <meta name="cover" content="' + cover_image + '"/>\n' + \
        '        <meta property="dcterms:date">' + date_creation.__str__() + '</meta>\n' + \
        '        <meta id="meta-language" property="dcterms:language">' + info['language'] + '</meta>\n' + \
        '    </metadata>\n'

    return metadata


def opf_manifest(oebp: Path, c_dict: dict) -> (str, list):
    toc_ncx = '        <item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml" />\n'
    toc_html = '        <item href="toc.xhtml" id="toc" media-type="application/xhtml+xml" properties="nav">\n'
    style_css = '        <item href="Styles/style.css" id="style.css" media-type="text/css" />\n'
    # notereplace_js = '        <item href="Misc/notereplace.js" id="notereplace.js" media-type="text/plain" />\n'

    fonts = ''
    for font_name in c_dict['fonts']:
        fonts += f'        <item href="Fonts/{font_name}" id="{font_name}" media-type="application/x-font-ttf" />\n'

    images = ''
    for t, img_id, is_ok, _, _, suffix, img_b64 in c_dict['imgs']:
        images += f'        <item href="Images/{img_id}.{suffix}" id="{img_id}" media-type="image/{suffix}"/>\n'
        r.wb(oebp/f'Images/{img_id}.{suffix}', r.load(img_b64, 'b64'))

    xhtmls = '' \
        '        <item href="Text/cover_info.xhtml" id="cover_info" media-type="application/xhtml+xml" />\n' + \
        '        <item href="Text/chaps_list.xhtml" id="chaps_list" media-type="application/xhtml+xml" />\n'

    chap_ids = [cid for pid, tags, parts in c_dict["chaps"] for cid in [pid]+[j[0] for j in parts]]
    for chap_id in chap_ids:
        xhtmls += f'        <item href="Text/{chap_id}.xhtml" id="{chap_id}" media-type="application/xhtml+xml"/>\n'

    manifest = \
        '    <manifest>\n' + \
        toc_ncx + \
        style_css + \
        fonts + \
        images + \
        xhtmls + \
        '    </manifest>\n'

    return manifest, chap_ids


def rand() -> str:
    import secrets
    return ''.join([secrets.token_hex(3)+'-' for i in range(3)])


def opf_spine(chap_ids: list) -> str:
    spine = '    <spine toc="ncx">\n' + \
            '        <itemref idref="cover_info"/>\n' + \
            '        <itemref idref="chaps_list"/>\n'
    for chap_id in chap_ids:
        spine += f'        <itemref idref="{chap_id}"/>\n'
    spine += '    </spine>\n'

    return spine


def epub_opf(oebp: Path, c_dict: dict) -> str:
    c_dict['info']['temp_d'] = str(uuid.uuid4())
    metadata = opf_metadata(c_dict)
    manifest, chap_ids = opf_manifest(oebp, c_dict)
    spine = opf_spine(chap_ids)
    guide = \
        '    <guide>\n' + \
        '        <reference href="toc.xhtml" title="Table of Contents" type="toc"></reference>\n' + \
        '    </guide>\n'

    return \
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + \
        '<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">\n' + \
        metadata + \
        manifest + \
        spine + \
        '</package>'


def toc_nav_map(c_dict: dict) -> str:

    index = [0]
    def nav(nid: str, text: str, indent=1, close=False) -> (str, str):
        nav_point =  \
            indent*'    ' + '<navPoint id="' + nid + '" playOrder="' + str(index[0]) + '">\n' + \
            indent*'    ' + '    <navLabel>\n' + \
            indent*'    ' + '        <text>' + text + '</text>\n' + \
            indent*'    ' + '    </navLabel>\n' + \
            indent*'    ' + '    <content src="Text/' + nid + '.xhtml" />\n'
        index[0] += 1
        return (nav_point + indent*'    ' + '</navPoint>\n') if close else nav_point

    nav_points = \
        nav('cover_info', 'cover', close=True) + \
        nav('chaps_list', 'table of content', close=True)

    for pid, tags, parts in c_dict["chaps"]:
        nav_points += nav(pid, pid+' '.join(tags))
        for j in parts:
            nav_points += nav(j[0], j[1], indent=2, close=True)
        nav_points += '    </navPoint>\n'

    nav_map = \
        '    <navMap>\n' + \
        nav_points + \
        '    </navMap>\n'

    return nav_map


def epub_toc(c_dict: dict) -> str:
    toc = \
        '<?xml version="1.0" encoding="utf-8"?>\n' + \
        '<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n' + \
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n' + \
        '    <head>\n' + \
        '        <meta name="dtb:uid" content="urn:uuid:'+c_dict['info']['temp_d']+'" />\n' + \
        '        <meta content="2" name="dtb:depth"/>\n' + \
        '        <meta content="0" name="dtb:totalPageCount"/>\n' + \
        '        <meta content="0" name="dtb:maxPageNumber"/>\n' + \
        '    </head>\n' +\
        '    <docTitle>\n' + \
        '        <text>' + c_dict['info']['title'] + '</text>\n' + \
        '    </docTitle>\n' + \
        '    <docAuthor>\n' + \
        '        <text>' + c_dict['info']['author'] + '</text>\n' + \
        '    </docAuthor>\n' + \
        toc_nav_map(c_dict) + \
        '</ncx>\n'

    return toc


def xhtml_embed(title: str, content: str):
    return \
        '<?xml version="1.0" encoding="utf-8"?>\n' + \
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n' + \
        '<html xmlns="http://www.w3.org/1999/xhtml">\n' + \
        '<head>\n' + \
        '    <link href="../Styles/style.css" rel="stylesheet" type="Text/css"/>\n' + \
        '    <title>' + title + '</title>\n' + \
        '</head>\n' + \
        '<body>\n' + \
        content + \
        '</body>\n' + \
        '</html>'


def epub_cover(c_dict: dict) -> str:

    info = c_dict['info']
    text = \
        '    <div style="text-align: center; padding: 0pt; margin: 0pt;">\n' + \
        '        <img width="1600" alt="cover" src="../Images/cover_0.' + c_dict['imgs'][0][5] + '"/>\n' + \
        '    </div>\n' + \
        '    <div class="title" style="margin: 5em 0em;">\n' + \
        '        <p class="h2" style="margin: 0;">' + info['title'] + '</p>\n' + \
        '        <p class="center" style="margin: 2em 0 0 0.3em; line-height: 1em;">\n' + \
        '            <span class="em06">author／</span>\n' + \
        '            <span class="tbox">' + info['author'] + '</span></p>\n' + \
        '        <p class="center" style="margin: 2em 0 0 0.3em; line-height: 1em;">\n' + \
        '            <span class="em06">illus／</span>\n' \
        '            <span class="tbox">' + info['illustrator'] + '</span></p>\n' + \
        '        <p class="center" style="margin: 2em 0 0 0.3em; line-height: 1em;">\n' \
        '            <span class="em06">' + str(info['date_creation'])[:-6] + '</span></p>\n' + \
        '        <p class="center" style="margin: 2em 0 0 0.3em; line-height: 1em;">\n' \
        '            <span class="em06">\n' \
        '                <a href="' + info['source_site'].removeprefix('...') + '">' + info['source_site'] + '</a>\n' \
        '            </span>\n' \
        '        </p>\n' + \
        '    </div>\n' + \
        '    <div>\n' + \
        '        <p class="h3">intro</p>\n' + \
        '        <p class="intro">──────────────</p>\n' + \
        ''.join([' '*8+f'<p class="intro">{i}</p>\n' for i in info['intro']]) + \
        '    </div>\n'

    # text += '    <div class="illus">\n'
    # for i in info['esj_img_srcs']:
    #     text += '        <img src="../Images/' + i[0] + '"/>\n'
    # text += '    </div>\n'
    return xhtml_embed('Cover', text)


def epub_clist(c_dict: dict):
    text = \
        '    <div class="em08 bold" style="margin: 3em 0em;">\n' + \
        '        <p class="h2" style="text-align: center;"><b>CONTENTS</b></p>\n'
    for pid, tags, parts in c_dict["chaps"]:
        text += f'        <p class="text1" style="text-align: center;"><a href="../Text/{pid}.xhtml"><span class="co0">{pid}</span></a></p>\n'
        for cid, title, _, _, _ in parts:
            text += f'        <p class="text1" style="text-align: center;"><a href="../Text/{cid}.xhtml"><span class="co0">{title}</span></a></p>\n'

    text += '    </div>\n'
    return xhtml_embed('table of content', text)


def content_text(chap_id: str, title: str, lines: list) -> str:

    text = \
        '    <div class="chap">\n' + \
        '        <p class="h2">' + title + '</p>\n\n'

    for line in lines:
        if line[0] == 'text':
            text += '        <p>' + line[1] + '</p>\n'
        elif line[0] == 'img':
            text += \
                f'        <div class="illus"><img alt="{line[1]}" src="../Images/{line[1]}.{line[5]}"/></div>\n'
        elif line[0] == 'error':
            loggerA.error(f'text block error: {chap_id}')

    text += '    </div>\n'
    return xhtml_embed(title, text)


def content_section(part_id: str, tags: list) -> str:
    text = '    <div class="chap">\n'
    for tag in tags:
        text += '        <p>' + tag + '</p>\n'
    text += '    </div>\n'
    return xhtml_embed(part_id, text)


def epub_write_chap(xhtmls: Path, c_dict: dict):
    for pid, tags, parts in c_dict['chaps']:
        r.wt(xhtmls / f'{pid}.xhtml', content_section(pid, tags))
        for cid, title, _, _, lines in parts:
            r.wt(xhtmls / f'{cid}.xhtml', content_text(cid, title, lines))


def epub_create(epub: Path, c_dict: dict):

    [c_dict['info'].update({k: '...'}) for k, v in c_dict['info'].items() if not v]
    oebp = r.mkdir(epub / "OEBPS")
    meta = r.mkdir(epub / "META-INF")
    r.mkdir(oebp / "Text")
    r.mkdir(oebp / "Fonts")
    r.mkdir(oebp / "Images")
    r.mkdir(oebp / "Styles")
    r.wt(oebp / 'Styles/style.css', css)
    r.wt(epub / "mimetype", epub_mimetype())
    r.wt(meta / "container.xml", epub_container())
    r.wt(oebp / "content.opf", epub_opf(oebp, c_dict))
    r.wt(oebp / "toc.ncx", epub_toc(c_dict))
    r.wt(oebp / 'Text/cover_info.xhtml', epub_cover(c_dict))
    r.wt(oebp / 'Text/chaps_list.xhtml', epub_clist(c_dict))

    epub_write_chap(oebp/'Text', c_dict)


def write_zip(path: Path, name):
    epub = zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED)
    for i in path.rglob('*'):
        epub.write(i, i.relative_to(path))
    epub.close()


# def build():
def build(bk_path: Path, c_dict: dict):
    try:
        epub_path = bk_path/'epub'
        if epub_path.exists():
            shutil.rmtree(epub_path)
            loggerA.warning("epub folder exist, cleaning")
        epub_create(epub_path, c_dict)

        write_zip(epub_path, bk_path/f'{c_dict["info"]["title"]}.epub')

    except:
        print(traceback.format_exc())

