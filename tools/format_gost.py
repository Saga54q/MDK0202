# -*- coding: utf-8 -*-
"""
Приведение отчётов по лабораторным работам к требованиям нормоконтроля
(ГОСТ 7.32-2017): A4, поля 30/15/20/20 мм, Times New Roman 14 пт,
межстрочный интервал 1,5, абзацный отступ 1,25 см, выравнивание по ширине,
нумерация страниц снизу по центру, подписи рисунков, названия таблиц.

Содержимое документов не изменяется: правится форматирование, добавляются
подписи рисунка и названий таблиц, а также колонтитул с номером страницы.
"""

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH as AL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt

TNR = "Times New Roman"
MONO = "Courier New"
BODY = dict(align=AL.JUSTIFY, first=Cm(1.25), ls=1.5, before=0, after=0)
HEAD = dict(align=AL.LEFT, first=Cm(1.25), ls=1.5, before=12, after=6, keep=True)
MONOBLOCK = dict(align=AL.LEFT, first=Cm(0), ls=1.0, before=6, after=6)
FIG_CAP = dict(align=AL.CENTER, first=Cm(0), ls=1.5, before=6, after=12)
TBL_CAP = dict(align=AL.LEFT, first=Cm(0), ls=1.5, before=6, after=6, keep=True)
CENTER = dict(align=AL.CENTER, first=Cm(0), ls=1.5, before=0, after=0)

TEXT_WIDTH = Mm(165)            # 210 - 30 - 15 = 165 мм — полоса набора

# порядок дочерних элементов по схеме OOXML (иначе Word ругается на файл)
ORDER = {
    "w:tblPr": ["w:tblStyle", "w:tblpPr", "w:tblOverlap", "w:bidiVisual",
                "w:tblStyleRowBandSize", "w:tblStyleColBandSize", "w:tblW", "w:jc",
                "w:tblCellSpacing", "w:tblInd", "w:tblBorders", "w:shd", "w:tblLayout",
                "w:tblCellMar", "w:tblLook", "w:tblCaption", "w:tblDescription"],
    "w:trPr": ["w:cnfStyle", "w:divId", "w:gridBefore", "w:gridAfter", "w:wBefore",
               "w:wAfter", "w:cantSplit", "w:trHeight", "w:tblHeader",
               "w:tblCellSpacing", "w:jc", "w:hidden"],
    "w:tcPr": ["w:cnfStyle", "w:tcW", "w:gridSpan", "w:hMerge", "w:vMerge",
               "w:tcBorders", "w:shd", "w:noWrap", "w:tcMar", "w:textDirection",
               "w:tcFitText", "w:vAlign", "w:hideMark"],
}


def insert_ordered(parent, element):
    """Вставить элемент в родителя с соблюдением порядка схемы OOXML."""
    order = ORDER["w:" + parent.tag.split("}")[-1]]
    rank = order.index("w:" + element.tag.split("}")[-1])
    for pos, child in enumerate(parent):
        tag = "w:" + child.tag.split("}")[-1]
        if tag in order and order.index(tag) > rank:
            parent.insert(pos, element)
            return element
    parent.append(element)
    return element


# ---------------------------------------------------------------- примитивы
def set_run(run, name=TNR, size=14, bold=None):
    run.font.name = name
    run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    rf = run._element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(attr), name)


def fmt_para(p, spec, name=TNR, size=14, bold=None):
    pf = p.paragraph_format
    pf.alignment = spec["align"]
    pf.first_line_indent = spec["first"]
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    pf.line_spacing = spec["ls"]
    pf.space_before = Pt(spec["before"])
    pf.space_after = Pt(spec["after"])
    pf.keep_with_next = spec.get("keep", False)
    for r in p.runs:
        set_run(r, name, size, bold)
    return p


def fill(p, lines, spec, bold=False, size=14):
    """Заменить содержимое абзаца строками (мягкие переносы внутри абзаца)."""
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    for i, line in enumerate(lines):
        if i:
            p.add_run().add_break()
        p.add_run(line)
    return fmt_para(p, spec, size=size, bold=bold)


def new_para(doc, text, spec, bold=False, size=14):
    p = doc.add_paragraph()
    p.add_run(text)
    return fmt_para(p, spec, bold=bold, size=size)


def page_field(paragraph):
    """Поле { PAGE } в колонтитуле."""
    for kind, text in (("begin", None), (None, " PAGE "), ("separate", None),
                       (None, "2"), ("end", None)):
        run = paragraph.add_run()
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText" if text.strip().startswith("PAGE") else "w:t")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._element.append(el)
        set_run(run)


def setup_section(doc):
    s = doc.sections[0]
    s.page_width, s.page_height = Mm(210), Mm(297)          # A4
    s.left_margin, s.right_margin = Cm(3.0), Cm(1.5)        # ГОСТ 7.32-2017
    s.top_margin, s.bottom_margin = Cm(2.0), Cm(2.0)
    s.header_distance, s.footer_distance = Cm(1.25), Cm(1.25)
    s.different_first_page_header_footer = True             # титул без номера
    for footer in (s.footer, s.first_page_footer):
        for p in list(footer.paragraphs)[1:]:
            p._element.getparent().remove(p._element)
        p = footer.paragraphs[0]
        for r in list(p.runs):
            r._element.getparent().remove(r._element)
    fmt_para(s.footer.paragraphs[0], CENTER, size=14)
    s.footer.paragraphs[0].paragraph_format.line_spacing = 1.0
    page_field(s.footer.paragraphs[0])


def setup_styles(doc):
    st = doc.styles["Normal"]
    st.font.name = TNR
    st.font.size = Pt(14)
    rf = st.element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(attr), TNR)
    pf = st.paragraph_format
    pf.alignment = AL.JUSTIFY
    pf.first_line_indent = Cm(1.25)
    pf.line_spacing = 1.5
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)


def fit_table_width(table, target=TEXT_WIDTH):
    """Ширина таблицы = полоса набора, столбцы — пропорционально исходным."""
    tbl = table._tbl
    cols = tbl.find(qn("w:tblGrid")).findall(qn("w:gridCol"))
    old = [int(c.get(qn("w:w"))) for c in cols]
    total = sum(old) or 1
    tw = int(target.twips)
    new = [max(600, round(w * tw / total)) for w in old]
    new[-1] += tw - sum(new)
    for c, w in zip(cols, new):
        c.set(qn("w:w"), str(w))
    tblPr = tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout"):
        el = tblPr.find(qn(tag))
        if el is not None:
            tblPr.remove(el)
    w_el = OxmlElement("w:tblW")
    w_el.set(qn("w:w"), str(tw))
    w_el.set(qn("w:type"), "dxa")
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    insert_ordered(tblPr, w_el)
    insert_ordered(tblPr, lay)
    for row, w in zip(table.rows, new):
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcW = tcPr.find(qn("w:tcW"))
            if tcW is not None:
                tcPr.remove(tcW)
            tcW = OxmlElement("w:tcW")
            tcW.set(qn("w:w"), str(w))
            tcW.set(qn("w:type"), "dxa")
            insert_ordered(tcPr, tcW)


def table_format(doc, idx, caption):
    """Название таблицы + оформление: 12 пт, одинарный интервал, шапка
    повторяется на новой странице, строки не разрываются."""
    t = doc.tables[idx]
    cap = new_para(doc, caption, TBL_CAP)
    t._tbl.addprevious(cap._p)
    for ri, row in enumerate(t.rows):
        for cell in row.cells:
            for p in cell.paragraphs:
                align = AL.CENTER if ri == 0 else (p.paragraph_format.alignment or AL.LEFT)
                fmt_para(p, dict(align=align, first=Cm(0), ls=1.0, before=2, after=2),
                         size=12, bold=True if ri == 0 else None)
    first_trPr = t.rows[0]._tr.get_or_add_trPr()
    insert_ordered(first_trPr, OxmlElement("w:cantSplit"))
    insert_ordered(first_trPr, OxmlElement("w:tblHeader"))
    for row in t.rows[1:]:
        insert_ordered(row._tr.get_or_add_trPr(), OxmlElement("w:cantSplit"))
    for row in t.rows:
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            mar = tcPr.find(qn("w:tcMar"))
            if mar is not None:
                tcPr.remove(mar)
            mar = OxmlElement("w:tcMar")
            for side, val in (("top", 40), ("bottom", 40), ("left", 80), ("right", 80)):
                el = OxmlElement(f"w:{side}")
                el.set(qn("w:w"), str(val))
                el.set(qn("w:type"), "dxa")
                mar.append(el)
            insert_ordered(tcPr, mar)
    fit_table_width(t)


def fix_images(doc):
    """Иллюстрации по центру, ширина не более полосы набора."""
    for shape in doc.inline_shapes:
        if shape.width > TEXT_WIDTH:
            ratio = shape.height / shape.width
            shape.width = TEXT_WIDTH
            shape.height = int(TEXT_WIDTH * ratio)


def drop_empty_body_paras(doc, first_heading_index):
    """Убрать пустые абзацы в теле документа: отступы задаются интервалами.
    Пустые абзацы шапки (до первого заголовка) сохраняются."""
    for i, p in enumerate(doc.paragraphs):
        if i <= first_heading_index:
            continue
        if p.text.strip():
            continue
        if p._p.findall(".//" + qn("w:drawing")) or p._p.findall(".//" + qn("w:pict")):
            continue
        p._element.getparent().remove(p._element)


# ------------------------------------------------------------------ ЛАБА 1
def lab1(src, dst):
    doc = Document(src)
    setup_styles(doc)
    setup_section(doc)

    ps = doc.paragraphs
    headings = {7, 14, 23, 26, 28, 31, 43, 47, 50}   # разделы и подразделы
    mono = {30, 45}                                  # дерево проекта и команды Git

    for i in (0, 1, 3):
        fmt_para(ps[i], dict(CENTER, after=6), bold=True)
    fill(ps[5], ("Студент: Сагадиев Амир",
                 "Группа: ИСП-23-19",
                 "Преподаватель: Кондров В. А."),
         dict(CENTER, before=12))

    for i, p in enumerate(ps):
        if i in (0, 1, 3, 5):
            continue
        if i in headings:
            fmt_para(p, HEAD, bold=True)
        elif i in mono:
            fmt_para(p, MONOBLOCK, name=MONO, size=12)
        elif i == 25:                                # абзац с диаграммой
            fmt_para(p, dict(align=AL.CENTER, first=Cm(0), ls=1.0, before=6, after=6,
                             keep=True))
        elif i == 51:                                # рамка для скриншота
            fmt_para(p, dict(align=AL.CENTER, first=Cm(0), ls=1.5, before=6, after=6),
                     bold=True)
        elif not p.text.strip():
            fmt_para(p, dict(align=p.paragraph_format.alignment, first=Cm(0), ls=1.5,
                             before=0, after=0))
        else:
            fmt_para(p, BODY)

    cap = new_para(doc, "Рисунок 1 – Диаграмма модульной структуры проекта "
                        "«Генератор случайных цитат»", FIG_CAP)
    ps[25]._p.addnext(cap._p)

    drop_empty_body_paras(doc, first_heading_index=7)
    fix_images(doc)
    table_format(doc, 0, "Таблица 1 – Описание модулей проекта")
    doc.save(dst)


# ------------------------------------------------------------------ ЛАБА 2
def lab2(src, dst):
    doc = Document(src)
    setup_styles(doc)
    setup_section(doc)

    ps = doc.paragraphs
    headings = {16, 21, 28, 31, 35, 41, 47, 48, 59, 67, 69, 70, 73}
    mono = {55, 56, 57, 58}                          # примеры сообщений коммитов
    img_paras = {75, 78, 81}                         # абзацы с иллюстрациями
    caps = {76, 79, 82}                              # подписи рисунков

    for i in (0, 5, 10):
        fmt_para(ps[i], dict(CENTER, after=6), bold=True)
    fill(ps[13], ("Студент: Сагадиев Амир", "Группа: ИСП-23-19"),
         dict(CENTER, before=12))
    fill(ps[14], ("Преподаватель: Кондров В. А.",), CENTER)

    for i, p in enumerate(ps):
        if i in (0, 5, 10, 13, 14):
            continue
        if i in caps:
            txt = p.text.strip().rstrip(".")
            txt = txt[0].upper() + txt[1:]
            fill(p, (txt,), FIG_CAP)
        elif i in headings:
            fmt_para(p, HEAD, bold=True)
        elif i in mono:
            fmt_para(p, MONOBLOCK, name=MONO, size=12)
        elif i in img_paras:
            fmt_para(p, dict(align=AL.CENTER, first=Cm(0), ls=1.0, before=6, after=0,
                             keep=True))
        elif not p.text.strip():
            fmt_para(p, dict(align=p.paragraph_format.alignment, first=Cm(0), ls=1.5,
                             before=0, after=0))
        else:
            fmt_para(p, BODY)

    drop_empty_body_paras(doc, first_heading_index=16)
    fix_images(doc)
    table_format(doc, 0, "Таблица 1 – Матрица артефактов проекта")
    table_format(doc, 1, "Таблица 2 – Мини-трекер проекта")
    doc.save(dst)


if __name__ == "__main__":
    lab1("Лабораторная_1_Генератор_случайных_цитат.docx",
         "out/Лабораторная_1_Генератор_случайных_цитат.docx")
    lab2("Лабораторная_2_Генератор_случайных_цитат_как_лаба_1.docx",
         "out/Лабораторная_2_Генератор_случайных_цитат_как_лаба_1.docx")
    print("готово")
