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


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "materials" / "vkr-draft-content.md"
OUT_DIR = ROOT / "build" / "docx"
OUT_DOCX = OUT_DIR / "vkr-draft-1.docx"

TITLE = "Разработка real-time интерфейса с поддержкой горизонтального масштабирования WebSocket-соединений для системы отслеживания задач"
STUDENT_FULL = "Зайцев Александр Сергеевич"
STUDENT_INSTR = "Зайцевым Александром Сергеевичем"
STUDENT_SHORT = "А.С. Зайцев"
GROUP = "4131з"
SUPERVISOR = "С.А. Рогачев"
SUPERVISOR_ROLE = "ст. преподаватель"
CITY_YEAR = "Санкт-Петербург 2026"


def set_cell_text(cell, text: str, *, size: int = 14, bold: bool = False, align=WD_ALIGN_PARAGRAPH.CENTER):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


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


def add_left(doc, text: str, *, size=14, bold=False, first_line=0, space_after=0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Cm(first_line)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold)
    return p


def add_title_page(doc: Document):
    add_centered(doc, "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ", size=14)
    add_centered(doc, "федеральное государственное автономное образовательное учреждение высшего образования", size=13)
    add_centered(doc, "«САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ", size=14)
    add_centered(doc, "АЭРОКОСМИЧЕСКОГО ПРИБОРОСТРОЕНИЯ»", size=14, space_after=18)

    table = doc.add_table(rows=4, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    clear_table_borders(table)
    widths = [Cm(6), Cm(5), Cm(5)]
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            cell.width = widths[i]
    set_cell_text(table.cell(0, 0), "ДОПУСТИТЬ К ЗАЩИТЕ", align=WD_ALIGN_PARAGRAPH.LEFT)
    set_cell_text(table.cell(1, 0), "Заведующий кафедрой № 43", align=WD_ALIGN_PARAGRAPH.LEFT)
    set_cell_text(table.cell(2, 0), "________________________", align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(table.cell(2, 1), "________________________", align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(table.cell(2, 2), "М.Ю. Охтилев", align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(table.cell(3, 0), "должность, уч. степень, звание", size=10)
    set_cell_text(table.cell(3, 1), "подпись, дата", size=10)
    set_cell_text(table.cell(3, 2), "инициалы, фамилия", size=10)

    for _ in range(2):
        doc.add_paragraph()

    add_centered(doc, "БАКАЛАВРСКАЯ РАБОТА", size=16, bold=True, space_after=24)
    add_centered(doc, "на тему", size=14)
    p = add_centered(doc, TITLE, size=14)
    p.paragraph_format.space_after = Pt(18)

    line_table = doc.add_table(rows=5, cols=3)
    clear_table_borders(line_table)
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
            set_cell_text(line_table.cell(r, c), value, size=10 if r in [1, 3] else 14)
            if r in [0, 2, 4] and c > 0:
                set_bottom_border(line_table.cell(r, c))

    doc.add_paragraph()
    sig = doc.add_table(rows=4, cols=3)
    clear_table_borders(sig)
    for row in sig.rows:
        row.cells[0].width = Cm(7)
        row.cells[1].width = Cm(4)
        row.cells[2].width = Cm(5)
    set_cell_text(sig.cell(0, 0), f"Студент группы № {GROUP}", size=12, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_cell_text(sig.cell(0, 1), "____________________", align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(sig.cell(0, 2), STUDENT_SHORT, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(sig.cell(1, 1), "подпись, дата", size=10)
    set_cell_text(sig.cell(1, 2), "инициалы, фамилия", size=10)
    set_cell_text(sig.cell(2, 0), "Руководитель", align=WD_ALIGN_PARAGRAPH.LEFT)
    set_cell_text(sig.cell(2, 1), "____________________", align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(sig.cell(2, 2), SUPERVISOR, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_text(sig.cell(3, 0), SUPERVISOR_ROLE, size=10)
    set_cell_text(sig.cell(3, 1), "подпись, дата", size=10)
    set_cell_text(sig.cell(3, 2), "инициалы, фамилия", size=10)

    for _ in range(2):
        doc.add_paragraph()
    add_centered(doc, CITY_YEAR)
    doc.add_page_break()


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


def add_toc(doc: Document):
    p = doc.add_heading("СОДЕРЖАНИЕ", level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    add_field(p, r'TOC \o "1-3" \h \z \u')
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


def add_code_block(doc: Document, code: str, language: str | None):
    if language == "mermaid":
        caption = "Рисунок — схема будет оформлена на следующем этапе верстки."
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        run = p.add_run(caption)
        set_run_font(run, size=12, italic=True)
        return
    for line in code.strip("\n").splitlines():
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.left_indent = Cm(1.25)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(line)
        set_run_font(run, size=10, name="Courier New")


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


def process_markdown(doc: Document, text: str):
    lines = text.splitlines()
    in_code = False
    code_lang = None
    code_lines: list[str] = []
    table_lines: list[str] = []
    table_idx = 1
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
                add_code_block(doc, "\n".join(code_lines), code_lang)
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
        "В приложении должны быть приведены фрагменты `docker-compose.thesis.yml`, `docker-compose.thesis.no-backplane.yml`, `upstreams.thesis.conf`, настройки SignalR с `AddStackExchangeRedis`, диагностического метода `GetConnectionDiagnosticsAsync`, компонента `RealtimeDebugBadge`, а также выводы автоматизированного сценария проверки.",
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
    doc = Document()
    setup_styles(doc)
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
    process_markdown(doc, SOURCE.read_text(encoding="utf-8"))
    add_appendices(doc)

    doc.save(OUT_DOCX)
    audit_docx(OUT_DOCX)
    print(OUT_DOCX)


if __name__ == "__main__":
    main()
