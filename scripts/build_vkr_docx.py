from __future__ import annotations

import re
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "materials" / "04-docx" / "vkr-draft-content.md"
OUT_DIR = ROOT / "build" / "docx"
OUT_DOCX = OUT_DIR / "vkr-draft-1.docx"
ASSET_DIR = OUT_DIR / "assets"

TITLE = "Разработка real-time интерфейса с поддержкой горизонтального масштабирования WebSocket-соединений для системы отслеживания задач"
STUDENT_FULL = "Зайцев Александр Сергеевич"
STUDENT_INSTR = "Зайцевым Александром Сергеевичем"
STUDENT_SHORT = "А.С. Зайцев"
GROUP = "4131з"
SUPERVISOR = "С.А. Рогачев"
SUPERVISOR_ROLE = "ст. преподаватель"
CITY_YEAR = "Санкт-Петербург 2026"
FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Times New Roman.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf")


def set_cell_text(cell, text: str, *, size: int = 14, bold: bool = False, align=WD_ALIGN_PARAGRAPH.CENTER):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def pil_font(size: int, *, bold: bool = False):
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(str(path), size=size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        width = draw.textbbox((0, 0), candidate, font=font)[2]
        if width <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    text: str,
    *,
    fill: str = "#F7F7F7",
    outline: str = "#222222",
    font=None,
    bold: bool = False,
):
    x1, y1, x2, y2 = xy
    font = font or pil_font(25, bold=bold)
    draw.rounded_rectangle(xy, radius=16, fill=fill, outline=outline, width=3)
    lines = wrap_text(draw, text, font, x2 - x1 - 28)
    line_height = font.size + 6
    total_height = line_height * len(lines)
    y = y1 + ((y2 - y1) - total_height) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        draw.text((x1 + ((x2 - x1) - (bbox[2] - bbox[0])) // 2, y), line, fill="#111111", font=font)
        y += line_height


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], *, color: str = "#111111", width: int = 4):
    draw.line([start, end], fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        sign = 1 if x2 >= x1 else -1
        head = [(x2, y2), (x2 - sign * 18, y2 - 10), (x2 - sign * 18, y2 + 10)]
    else:
        sign = 1 if y2 >= y1 else -1
        head = [(x2, y2), (x2 - 10, y2 - sign * 18), (x2 + 10, y2 - sign * 18)]
    draw.polygon(head, fill=color)


def add_figure_title(draw: ImageDraw.ImageDraw, title: str):
    font = pil_font(32, bold=True)
    bbox = draw.textbbox((0, 0), title, font=font)
    draw.text(((1600 - (bbox[2] - bbox[0])) // 2, 30), title, fill="#111111", font=font)


def create_single_node_figure(path: Path):
    img = Image.new("RGB", (1600, 900), "white")
    draw = ImageDraw.Draw(img)
    add_figure_title(draw, "Исходная single-node архитектура")
    node_fill = "#EEF3FA"
    service_fill = "#F9F0DF"
    data_fill = "#EAF6EA"
    draw_box(draw, (90, 170, 330, 280), "Клиент A", fill=node_fill)
    draw_box(draw, (90, 420, 330, 530), "Клиент B", fill=node_fill)
    draw_box(draw, (470, 300, 710, 410), "nginx", fill="#F3F3F3", bold=True)
    draw_box(draw, (850, 300, 1130, 410), "app-api", fill=service_fill, bold=True)
    draw_box(draw, (1210, 160, 1510, 280), "ReportPageHub", fill="#FCECEB")
    draw_box(draw, (1210, 360, 1510, 480), "Локальные группы SignalR", fill="#FCECEB")
    draw_box(draw, (1210, 570, 1510, 690), "PostgreSQL", fill=data_fill)
    draw_arrow(draw, (330, 225), (470, 335))
    draw_arrow(draw, (330, 475), (470, 375))
    draw_arrow(draw, (710, 355), (850, 355))
    draw_arrow(draw, (1130, 330), (1210, 220))
    draw_arrow(draw, (1130, 365), (1210, 420))
    draw_arrow(draw, (1130, 390), (1210, 630))
    note_font = pil_font(24)
    note = "Состояние соединений и групп хранится в памяти одного серверного процесса."
    draw.rounded_rectangle((120, 760, 1480, 835), radius=14, fill="#FFF8D6", outline="#D2B43A", width=2)
    draw.text((170, 785), note, fill="#111111", font=note_font)
    img.save(path)


def create_scaleout_figure(path: Path):
    img = Image.new("RGB", (1600, 900), "white")
    draw = ImageDraw.Draw(img)
    add_figure_title(draw, "Целевая multi-instance архитектура")
    node_fill = "#EEF3FA"
    service_fill = "#F9F0DF"
    data_fill = "#EAF6EA"
    broker_fill = "#E9F7F7"
    draw_box(draw, (80, 170, 320, 280), "Клиент A", fill=node_fill)
    draw_box(draw, (80, 500, 320, 610), "Клиент B", fill=node_fill)
    draw_box(draw, (440, 330, 680, 450), "nginx", fill="#F3F3F3", bold=True)
    draw_box(draw, (820, 180, 1110, 300), "app-api-1", fill=service_fill, bold=True)
    draw_box(draw, (820, 500, 1110, 620), "app-api-2", fill=service_fill, bold=True)
    draw_box(draw, (1260, 330, 1510, 450), "Redis backplane", fill=broker_fill, bold=True)
    draw_box(draw, (1260, 650, 1510, 770), "PostgreSQL", fill=data_fill)
    draw_arrow(draw, (320, 225), (440, 360))
    draw_arrow(draw, (320, 555), (440, 420))
    draw_arrow(draw, (680, 360), (820, 240))
    draw_arrow(draw, (680, 420), (820, 560))
    draw_arrow(draw, (1110, 240), (1260, 360), color="#0A6E73")
    draw_arrow(draw, (1260, 420), (1110, 560), color="#0A6E73")
    draw_arrow(draw, (1110, 270), (1260, 690), color="#4C7A38")
    draw_arrow(draw, (1110, 590), (1260, 730), color="#4C7A38")
    note_font = pil_font(24)
    note = "Redis backplane передает SignalR-события между экземплярами app-api."
    draw.rounded_rectangle((120, 790, 1480, 855), radius=14, fill="#FFF8D6", outline="#D2B43A", width=2)
    draw.text((220, 812), note, fill="#111111", font=note_font)
    img.save(path)


def create_event_flow_figure(path: Path):
    img = Image.new("RGB", (1600, 900), "white")
    draw = ImageDraw.Draw(img)
    add_figure_title(draw, "Поток межузловой доставки события")
    labels = ["Клиент A", "app-api-1", "Redis backplane", "app-api-2", "Клиент B"]
    x_positions = [120, 450, 780, 1110, 1390]
    top = 150
    bottom = 760
    font = pil_font(24, bold=True)
    small = pil_font(21)
    for x, label in zip(x_positions, labels):
        draw_box(draw, (x - 105, 95, x + 105, 165), label, fill="#EEF3FA" if "Клиент" in label else "#F9F0DF")
        draw.line((x, top, x, bottom), fill="#999999", width=2)
    steps = [
        (0, 1, 230, "1. Изменение отчета"),
        (1, 1, 315, "2. Сохранение состояния"),
        (1, 2, 400, "3. Публикация события группы"),
        (2, 3, 485, "4. Межузловая доставка"),
        (3, 4, 570, "5. ReceiveReportPatch"),
    ]
    for src, dst, y, label in steps:
        if src == dst:
            x = x_positions[src]
            draw.arc((x + 30, y - 25, x + 170, y + 45), start=90, end=270, fill="#111111", width=4)
            draw_arrow(draw, (x + 40, y + 35), (x + 35, y + 34), width=4)
            draw.text((x + 80, y - 20), label, fill="#111111", font=small)
        else:
            draw_arrow(draw, (x_positions[src] + 30, y), (x_positions[dst] - 30, y), color="#0A6E73")
            mid = (x_positions[src] + x_positions[dst]) // 2
            bbox = draw.textbbox((0, 0), label, font=small)
            draw.text((mid - (bbox[2] - bbox[0]) // 2, y - 35), label, fill="#111111", font=small)
    draw.rounded_rectangle((145, 795, 1455, 855), radius=14, fill="#FFF8D6", outline="#D2B43A", width=2)
    note = "Ключевой проверяемый факт: клиент B получает событие, хотя подключен к другому узлу."
    bbox = draw.textbbox((0, 0), note, font=small)
    draw.text(((1600 - (bbox[2] - bbox[0])) // 2, 814), note, fill="#111111", font=small)
    img.save(path)


def ensure_figures() -> list[Path]:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    figures = [
        ASSET_DIR / "figure-1-single-node.png",
        ASSET_DIR / "figure-2-scaleout.png",
        ASSET_DIR / "figure-3-event-flow.png",
    ]
    create_single_node_figure(figures[0])
    create_scaleout_figure(figures[1])
    create_event_flow_figure(figures[2])
    return figures


def set_cell_borders(cell, **kwargs):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        edge_data = kwargs.get(edge)
        tag = "w:{}".format(edge)
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        if edge_data is None:
            element.set(qn("w:val"), "nil")
            continue
        for key, value in edge_data.items():
            element.set(qn(f"w:{key}"), str(value))


def clear_table_borders(table):
    for row in table.rows:
        for cell in row.cells:
            set_cell_borders(cell, top=None, left=None, bottom=None, right=None, insideH=None, insideV=None)


def set_bottom_border(cell):
    set_cell_borders(
        cell,
        top=None,
        left=None,
        right=None,
        insideH=None,
        insideV=None,
        bottom={"val": "single", "sz": "6", "space": "0", "color": "000000"},
    )


def set_page_margins(section):
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)


def set_run_font(run, *, size=14, bold=False, italic=False, name="Times New Roman"):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def setup_styles(doc: Document):
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(14)
    normal.paragraph_format.first_line_indent = Cm(1.25)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for name, size in [("Heading 1", 14), ("Heading 2", 14), ("Heading 3", 14)]:
        style = styles[name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = None
        style.paragraph_format.first_line_indent = Cm(0)
        style.paragraph_format.line_spacing = 1.5
        style.paragraph_format.space_before = Pt(12 if name == "Heading 1" else 6)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    for name in ["Title", "Subtitle"]:
        style = styles[name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")


def add_page_number_footer(section):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)
    set_run_font(run, size=12)


def enable_field_update_on_open(doc: Document):
    settings = doc.settings.element
    existing = settings.find(qn("w:updateFields"))
    if existing is None:
        existing = OxmlElement("w:updateFields")
        settings.append(existing)
    existing.set(qn("w:val"), "true")


def set_start_page_number(section, start: int):
    sect_pr = section._sectPr
    pg_num_type = sect_pr.find(qn("w:pgNumType"))
    if pg_num_type is None:
        pg_num_type = OxmlElement("w:pgNumType")
        sect_pr.append(pg_num_type)
    pg_num_type.set(qn("w:start"), str(start))


def add_centered(doc, text: str, *, size=14, bold=False, space_after=0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold)
    return p


def add_spacer(doc, points: int):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(points)
    return p


def add_left(doc, text: str, *, size=14, bold=False, first_line=0, space_after=0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Cm(first_line)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold)
    return p


def set_table_cell_margins(table, margin_twips: int = 0):
    for row in table.rows:
        for cell in row.cells:
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_mar = tc_pr.first_child_found_in("w:tcMar")
            if tc_mar is None:
                tc_mar = OxmlElement("w:tcMar")
                tc_pr.append(tc_mar)
            for side in ("top", "left", "bottom", "right"):
                node = tc_mar.find(qn(f"w:{side}"))
                if node is None:
                    node = OxmlElement(f"w:{side}")
                    tc_mar.append(node)
                node.set(qn("w:w"), str(margin_twips))
                node.set(qn("w:type"), "dxa")


def add_title_page(doc: Document):
    section = doc.sections[-1]
    section.top_margin = Cm(1.0)
    section.bottom_margin = Cm(0.8)

    add_centered(doc, "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ", size=11)
    add_centered(doc, "федеральное государственное автономное образовательное учреждение высшего образования", size=10)
    add_centered(doc, "«САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ", size=11)
    add_centered(doc, "АЭРОКОСМИЧЕСКОГО ПРИБОРОСТРОЕНИЯ»", size=11, space_after=4)

    table = doc.add_table(rows=4, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    clear_table_borders(table)
    set_table_cell_margins(table, 0)
    widths = [Cm(6), Cm(5), Cm(5)]
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            cell.width = widths[i]
    set_cell_text(table.cell(0, 0), "ДОПУСТИТЬ К ЗАЩИТЕ", size=10, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_cell_text(table.cell(1, 0), "Заведующий кафедрой № 43", size=10, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_cell_text(table.cell(2, 0), "________________________", size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(table.cell(2, 1), "________________________", size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(table.cell(2, 2), "М.Ю. Охтилев", size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(table.cell(3, 0), "должность, уч. степень, звание", size=7)
    set_cell_text(table.cell(3, 1), "подпись, дата", size=7)
    set_cell_text(table.cell(3, 2), "инициалы, фамилия", size=7)

    add_spacer(doc, 4)

    add_centered(doc, "БАКАЛАВРСКАЯ РАБОТА", size=14, bold=True, space_after=4)
    add_centered(doc, "на тему", size=12)
    p = add_centered(doc, TITLE, size=12)
    p.paragraph_format.space_after = Pt(4)

    line_table = doc.add_table(rows=5, cols=3)
    clear_table_borders(line_table)
    set_table_cell_margins(line_table, 0)
    for row in line_table.rows:
        for cell in row.cells:
            cell.width = Cm(5.2)
    rows = [
        ("выполнена", STUDENT_INSTR, ""),
        ("", "фамилия, имя, отчество студента в творительном падеже", ""),
        ("по направлению подготовки", "09.03.04", "Программная инженерия"),
        ("", "код", "наименование направления"),
        ("направленности", "02", "Проектирование программных систем"),
    ]
    for r, values in enumerate(rows):
        for c, value in enumerate(values):
            set_cell_text(line_table.cell(r, c), value, size=7 if r in [1, 3] else 10)
            if r in [0, 2, 4] and c > 0:
                set_bottom_border(line_table.cell(r, c))

    add_spacer(doc, 4)
    sig = doc.add_table(rows=4, cols=3)
    clear_table_borders(sig)
    set_table_cell_margins(sig, 0)
    for row in sig.rows:
        row.cells[0].width = Cm(7)
        row.cells[1].width = Cm(4)
        row.cells[2].width = Cm(5)
    set_cell_text(sig.cell(0, 0), f"Студент группы № {GROUP}", size=10, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_cell_text(sig.cell(0, 1), "____________________", size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(sig.cell(0, 2), STUDENT_SHORT, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(sig.cell(1, 1), "подпись, дата", size=7)
    set_cell_text(sig.cell(1, 2), "инициалы, фамилия", size=7)
    set_cell_text(sig.cell(2, 0), "Руководитель", size=10, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_cell_text(sig.cell(2, 1), "____________________", size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(sig.cell(2, 2), SUPERVISOR, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(sig.cell(3, 0), SUPERVISOR_ROLE, size=7)
    set_cell_text(sig.cell(3, 1), "подпись, дата", size=7)
    set_cell_text(sig.cell(3, 2), "инициалы, фамилия", size=7)

    add_spacer(doc, 4)
    add_centered(doc, CITY_YEAR, size=10)
    doc.add_page_break()

    set_page_margins(section)


def add_assignment_page(doc: Document):
    add_centered(doc, "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ", size=14)
    add_centered(doc, "федеральное государственное автономное образовательное учреждение высшего образования", size=13)
    add_centered(doc, "«САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ", size=14)
    add_centered(doc, "АЭРОКОСМИЧЕСКОГО ПРИБОРОСТРОЕНИЯ»", size=14, space_after=18)
    add_left(doc, "УТВЕРЖДАЮ", bold=True)
    add_left(doc, "Заведующий кафедрой №43 ____________________ М.Ю. Охтилев", first_line=0)
    add_centered(doc, "ЗАДАНИЕ НА ВЫПОЛНЕНИЕ БАКАЛАВРСКОЙ РАБОТЫ", size=16, bold=True, space_after=14)
    add_left(doc, f"студенту группы {GROUP} {STUDENT_FULL}", first_line=0)
    add_left(doc, f"на тему: {TITLE}", first_line=0)
    add_left(doc, "утвержденную приказом ГУАП от «___» __________ 2026 г. № __________", first_line=0)
    add_left(doc, "Цель работы: разработать и исследовать real-time интерфейс для системы отслеживания задач, в котором WebSocket-соединения обслуживаются несколькими экземплярами серверного приложения, а события об изменении сущностей корректно доставляются клиентам независимо от узла подключения.", first_line=0)
    add_left(doc, "Задачи, подлежащие решению: проанализировать предметную область и подходы к масштабированию WebSocket-соединений; исследовать исходную реализацию real-time контура; спроектировать распределенную архитектуру с межузловой доставкой событий; реализовать решение в отдельной ветке проекта; подготовить стенд и провести испытания.", first_line=0)
    add_left(doc, "Содержание работы (основные разделы): анализ предметной области, постановка задачи, проектирование масштабируемого real-time контура, реализация, испытания и оценка результатов.", first_line=0)
    add_left(doc, "Срок сдачи работы «___» __________ 2026 г.", first_line=0)
    doc.add_paragraph()
    add_left(doc, f"Руководитель {SUPERVISOR_ROLE} ____________________ {SUPERVISOR}", first_line=0)
    add_left(doc, f"Задание принял к исполнению студент группы № {GROUP} ____________________ {STUDENT_SHORT}", first_line=0)


def add_field(paragraph, instr_text: str):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instr_text
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "Обновите поле в Word"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(text)
    run._r.append(fld_end)
    set_run_font(run)


def add_abstract(doc: Document):
    p = doc.add_heading("РЕФЕРАТ", level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    facts = (
        "Выпускная квалификационная работа содержит введение, пять глав, заключение, "
        "список использованных источников из 15 наименований и приложения. "
        "Количество страниц, рисунков и таблиц уточняется после финальной верстки."
    )
    add_body_paragraph(doc, facts)
    add_body_paragraph(
        doc,
        "Ключевые слова: real-time интерфейс, WebSocket, SignalR, горизонтальное масштабирование, Redis backplane, система отслеживания задач, межузловая доставка событий.",
    )
    add_body_paragraph(
        doc,
        "Актуальность работы обусловлена необходимостью обеспечения корректного real-time взаимодействия пользователей системы отслеживания задач при переходе от одного экземпляра серверного приложения к многосерверной конфигурации.",
    )
    add_body_paragraph(
        doc,
        "Цель работы — разработать и исследовать real-time интерфейс для системы отслеживания задач, в котором WebSocket-соединения обслуживаются несколькими экземплярами серверного приложения, а события об изменении сущностей корректно доставляются клиентам независимо от узла подключения.",
    )
    add_body_paragraph(
        doc,
        "Полученные результаты: разработан распределенный real-time контур на базе SignalR и Redis backplane, подготовлен воспроизводимый multi-instance стенд, реализованы диагностические средства и проведена экспериментальная проверка межузловой доставки событий.",
    )
    doc.add_page_break()


def add_toc_line(doc: Document, title: str, page: int, *, level: int = 1):
    max_len = 82 if level == 1 else 76
    text = title
    dots = "." * max(4, max_len - len(text))
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.left_indent = Cm(0 if level == 1 else 0.75)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(f"{text} {dots} {page}")
    set_run_font(run, size=11, bold=level == 1)


def add_toc(doc: Document):
    p = doc.add_heading("СОДЕРЖАНИЕ", level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    entries = [
        (1, "РЕФЕРАТ", 1),
        (1, "ПЕРЕЧЕНЬ СОКРАЩЕНИЙ И ОБОЗНАЧЕНИЙ", 3),
        (1, "ВВЕДЕНИЕ", 4),
        (1, "1. Анализ предметной области и существующих подходов", 7),
        (2, "1.1 Real-time взаимодействие в системах отслеживания задач", 7),
        (2, "1.2 WebSocket и SignalR как основа real-time контура", 7),
        (2, "1.3 Ограничение single-node WebSocket-архитектуры", 8),
        (2, "1.4 Сравнение подходов к масштабированию", 9),
        (2, "1.5 Вывод по главе", 10),
        (1, "2. Анализ целевой системы и постановка задачи", 11),
        (2, "2.1 Характеристика целевой системы", 11),
        (2, "2.2 Исходная реализация real-time взаимодействия", 11),
        (2, "2.3 Требования к разрабатываемому решению", 12),
        (2, "2.4 Постановка задачи", 13),
        (1, "3. Проектирование масштабируемого real-time контура", 14),
        (2, "3.1 Исходная архитектура", 14),
        (2, "3.2 Целевая архитектура", 14),
        (2, "3.3 Поток real-time события", 15),
        (2, "3.4 Модель групп и повторной подписки", 16),
        (2, "3.5 Диагностический контур", 17),
        (1, "4. Реализация решения в целевой системе", 18),
        (2, "4.1 Организация работ", 18),
        (2, "4.2 Изменения backend", 18),
        (2, "4.3 Проверочный клиент", 19),
        (2, "4.4 Инфраструктурные изменения", 19),
        (2, "4.5 Автоматизированный сценарий проверки", 20),
        (1, "5. Испытания и оценка результатов", 22),
        (2, "5.1 Цель и программа испытаний", 22),
        (2, "5.2 Стенд испытаний", 22),
        (2, "5.3 Результат без Redis backplane", 23),
        (2, "5.4 Результат с Redis backplane", 23),
        (2, "5.5 Сравнительная таблица результатов", 24),
        (2, "5.6 Проверка входной точки стенда", 24),
        (2, "5.7 Ограничения эксперимента", 24),
        (2, "5.8 Вывод по испытаниям", 25),
        (1, "ЗАКЛЮЧЕНИЕ", 25),
        (1, "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", 27),
        (1, "ПРИЛОЖЕНИЕ А", 29),
    ]
    for level, title, page in entries:
        add_toc_line(doc, title, page, level=level)
    doc.add_page_break()


def add_abbreviations(doc: Document):
    p = doc.add_heading("ПЕРЕЧЕНЬ СОКРАЩЕНИЙ И ОБОЗНАЧЕНИЙ", level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    data = [
        ("API", "Application Programming Interface, программный интерфейс приложения"),
        ("ASP.NET Core", "платформа для разработки веб-приложений на языке C#"),
        ("HTTP", "HyperText Transfer Protocol, протокол передачи гипертекста"),
        ("JSON", "JavaScript Object Notation, текстовый формат обмена данными"),
        ("nginx", "обратный прокси-сервер и балансировщик нагрузки"),
        ("Redis", "система хранения данных в памяти, используемая как backplane"),
        ("SignalR", "библиотека ASP.NET Core для real-time взаимодействия"),
        ("UI", "User Interface, пользовательский интерфейс"),
        ("URL", "Uniform Resource Locator, адрес ресурса"),
        ("WebSocket", "сетевой протокол двусторонней связи поверх одного TCP-соединения"),
        ("ВКР", "выпускная квалификационная работа"),
    ]
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.columns[0].width = Cm(4)
    table.columns[1].width = Cm(12)
    set_cell_text(table.cell(0, 0), "Сокращение", bold=True)
    set_cell_text(table.cell(0, 1), "Расшифровка", bold=True)
    for abbr, meaning in data:
        cells = table.add_row().cells
        set_cell_text(cells[0], abbr, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_text(cells[1], meaning, align=WD_ALIGN_PARAGRAPH.LEFT)
    doc.add_page_break()


def add_body_paragraph(doc: Document, text: str):
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.line_spacing = 1.5
    for part in re.split(r"(`[^`]+`)", text):
        if not part:
            continue
        run = p.add_run(part[1:-1] if part.startswith("`") and part.endswith("`") else part)
        set_run_font(run, name="Courier New" if part.startswith("`") and part.endswith("`") else "Times New Roman")
    return p


def add_list_item(doc: Document, text: str, numbered=True):
    style = "List Number" if numbered else "List Bullet"
    p = doc.add_paragraph(style=style)
    p.paragraph_format.left_indent = Cm(1.25)
    p.paragraph_format.first_line_indent = Cm(-0.5)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    set_run_font(run)


def add_figure(doc: Document, image_path: Path, caption: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run()
    run.add_picture(str(image_path), width=Cm(15.5))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = Cm(0)
    cap.paragraph_format.space_after = Pt(6)
    cap_run = cap.add_run(caption)
    set_run_font(cap_run, size=12, italic=True)


def add_code_block(doc: Document, code: str, language: str | None, figure_paths: list[Path], figure_idx: int) -> int:
    if language == "mermaid":
        captions = [
            "Рисунок 1 — Исходная single-node архитектура real-time контура",
            "Рисунок 2 — Целевая multi-instance архитектура с Redis backplane",
            "Рисунок 3 — Последовательность межузловой доставки события ReceiveReportPatch",
        ]
        if figure_idx < len(figure_paths):
            add_figure(doc, figure_paths[figure_idx], captions[figure_idx])
        return figure_idx + 1
    for line in code.strip("\n").splitlines():
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.left_indent = Cm(1.25)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(line)
        set_run_font(run, size=10, name="Courier New")
    return figure_idx


def add_markdown_table(doc: Document, lines: list[str], table_idx: int) -> int:
    rows = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue
        rows.append(cells)
    if not rows:
        return table_idx

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
    cap.paragraph_format.first_line_indent = Cm(0)
    run = cap.add_run(f"Таблица {table_idx} — {rows[0][0] if rows else 'Сравнительные данные'}")
    set_run_font(run, size=12, bold=True)

    table = doc.add_table(rows=1, cols=len(rows[0]))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, text in enumerate(rows[0]):
        set_cell_text(table.cell(0, c), text, size=11, bold=True)
    for row in rows[1:]:
        cells = table.add_row().cells
        for c, text in enumerate(row[: len(cells)]):
            set_cell_text(cells[c], text, size=11, align=WD_ALIGN_PARAGRAPH.LEFT)
    return table_idx + 1


def add_sources_as_numbered_list(doc: Document, source_lines: list[str]):
    p = doc.add_heading("СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for line in source_lines:
        m = re.match(r"\d+\.\s+(.*)", line.strip())
        if not m:
            continue
        add_list_item(doc, m.group(1), numbered=True)


def process_markdown(doc: Document, text: str, figure_paths: list[Path]):
    lines = text.splitlines()
    in_code = False
    code_lang = None
    code_lines: list[str] = []
    table_lines: list[str] = []
    table_idx = 1
    figure_idx = 0
    skip_until_main = True
    in_sources = False
    source_lines: list[str] = []

    def flush_table():
        nonlocal table_lines, table_idx
        if table_lines:
            table_idx = add_markdown_table(doc, table_lines, table_idx)
            table_lines = []

    for raw in lines:
        line = raw.rstrip()

        if skip_until_main:
            if line.strip() == "## Введение":
                skip_until_main = False
            else:
                continue

        if line.startswith("## Список рисунков") or line.startswith("## Технические приложения") or line.startswith("## Что нужно сделать"):
            break

        if in_code:
            if line.startswith("```"):
                figure_idx = add_code_block(doc, "\n".join(code_lines), code_lang, figure_paths, figure_idx)
                in_code = False
                code_lang = None
                code_lines = []
            else:
                code_lines.append(line)
            continue

        if line.startswith("```"):
            flush_table()
            in_code = True
            code_lang = line.strip("`").strip() or None
            code_lines = []
            continue

        if line.strip().startswith("|"):
            table_lines.append(line)
            continue
        flush_table()

        if not line.strip():
            continue

        if line.strip() == "## Список использованных источников":
            in_sources = True
            continue

        if in_sources:
            if re.match(r"\d+\.\s+", line.strip()):
                source_lines.append(line.strip())
            continue

        if line.startswith("## "):
            heading = line[3:].strip()
            if heading not in {"Введение", "Заключение"}:
                doc.add_page_break()
            p = doc.add_heading(heading.upper() if heading in {"Введение", "Заключение"} else heading, level=1)
            if heading in {"Введение", "Заключение"}:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue

        if line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=2)
            continue

        numbered_match = re.match(r"^(\d+)\.\s+(.*)", line.strip())
        bullet_match = re.match(r"^[-*]\s+(.*)", line.strip())
        if numbered_match:
            add_list_item(doc, numbered_match.group(2), numbered=True)
        elif bullet_match:
            add_list_item(doc, bullet_match.group(1), numbered=False)
        else:
            add_body_paragraph(doc, line)

    flush_table()
    if source_lines:
        doc.add_page_break()
        add_sources_as_numbered_list(doc, source_lines)


def add_appendices(doc: Document):
    doc.add_page_break()
    p = doc.add_heading("ПРИЛОЖЕНИЕ А", level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_centered(doc, "Фрагменты конфигурации стенда и результаты испытаний", bold=True)
    add_body_paragraph(
        doc,
        "В приложении должны быть приведены фрагменты `docker-compose.thesis.yml`, `docker-compose.thesis.no-backplane.yml`, `upstreams.thesis.conf`, настройки SignalR с `AddStackExchangeRedis`, диагностического метода `GetConnectionDiagnosticsAsync`, минимального проверочного клиента, а также выводы автоматизированного сценария проверки.",
    )
    add_body_paragraph(
        doc,
        "На текущем этапе приложения оставлены как структурная заготовка. Полные листинги целесообразно добавить после согласования объема основного текста.",
    )


def audit_docx(path: Path):
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        required = {
            "word/document.xml",
            "word/styles.xml",
            "word/numbering.xml",
            "[Content_Types].xml",
        }
        missing = required - names
        if missing:
            raise RuntimeError(f"Missing OOXML parts: {sorted(missing)}")
        text = zf.read("word/document.xml").decode("utf-8", errors="ignore")
        for marker in ["", "turn0", "TODO", "Deep Research", "ChatGPT"]:
            if marker in text:
                raise RuntimeError(f"Forbidden marker in document.xml: {marker}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    figure_paths = ensure_figures()
    doc = Document()
    setup_styles(doc)
    enable_field_update_on_open(doc)
    set_page_margins(doc.sections[0])
    doc.sections[0].footer.is_linked_to_previous = False

    add_title_page(doc)
    add_assignment_page(doc)

    body_section = doc.add_section(WD_SECTION.NEW_PAGE)
    set_page_margins(body_section)
    set_start_page_number(body_section, 1)
    add_page_number_footer(body_section)

    add_abstract(doc)
    add_toc(doc)
    add_abbreviations(doc)
    process_markdown(doc, SOURCE.read_text(encoding="utf-8"), figure_paths)
    add_appendices(doc)

    doc.save(OUT_DOCX)
    audit_docx(OUT_DOCX)
    print(OUT_DOCX)


if __name__ == "__main__":
    main()
