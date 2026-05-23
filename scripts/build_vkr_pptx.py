from __future__ import annotations

import html
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "pptx"
OUT_PPTX = OUT_DIR / "vkr-defense-draft.pptx"
PRACTICE_OUT_PPTX = OUT_DIR / "practice-defense-draft.pptx"
DASHBOARD_IMAGE = ROOT / "materials" / "04-docx" / "assets" / "interface-dashboard.png"
REPORT_IMAGE = ROOT / "materials" / "04-docx" / "assets" / "interface-report-page.png"
MEDIA_IMAGES = {
    "interface-dashboard.png": DASHBOARD_IMAGE,
    "interface-report-page.png": REPORT_IMAGE,
}

SLIDE_W = 12_192_000
SLIDE_H = 6_858_000
EMU = 914_400

BG = "F8FAFA"
INK = "1A2730"
MUTED = "5E6A75"
ACCENT = "14A085"
ACCENT_2 = "6366F1"
PANEL = "FFFFFF"
SOFT = "E6F4F1"
IRIS_SOFT = "EEF0FE"
WARN = "FEF3C7"
DANGER_SOFT = "FEE2E2"
DANGER = "B91C1C"
HAIR = "E3E7EB"
VKR_SUPERVISOR_LINE = "Руководитель: канд. техн. наук, доцент А. В. Фомин"
PRACTICE_SUPERVISOR_LINE = "Руководитель: ст. преподаватель С. А. Рогачев"


def e(value: str) -> str:
    return html.escape(value, quote=False)


def inch(value: float) -> int:
    return round(value * EMU)


def tx_paragraph(text: str, *, size: int = 24, color: str = INK, bold: bool = False, align: str = "l") -> str:
    lines = text.split("\n")
    paras = []
    for line in lines:
        paras.append(
            f"""
            <a:p>
              <a:pPr algn="{align}"/>
              <a:r>
                <a:rPr lang="ru-RU" sz="{size * 100}" b="{1 if bold else 0}">
                  <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
                  <a:latin typeface="Verdana"/>
                  <a:cs typeface="Verdana"/>
                </a:rPr>
                <a:t>{e(line)}</a:t>
              </a:r>
            </a:p>"""
        )
    return "\n".join(paras)


def shape(
    sid: int,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str = "",
    *,
    fill: str = PANEL,
    line: str = "E3E7EB",
    text_color: str = INK,
    size: int = 24,
    bold: bool = False,
    radius: bool = True,
    align: str = "l",
    margin: int = 14,
) -> str:
    geom = "roundRect" if radius else "rect"
    fill_xml = f"<a:solidFill><a:srgbClr val=\"{fill}\"/></a:solidFill>" if fill else "<a:noFill/>"
    line_xml = f"<a:ln w=\"12700\"><a:solidFill><a:srgbClr val=\"{line}\"/></a:solidFill></a:ln>" if line else "<a:ln><a:noFill/></a:ln>"
    text_xml = tx_paragraph(text, size=size, color=text_color, bold=bold, align=align) if text else "<a:p/>"
    return f"""
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{sid}" name="Shape {sid}"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm><a:off x="{inch(x)}" y="{inch(y)}"/><a:ext cx="{inch(w)}" cy="{inch(h)}"/></a:xfrm>
          <a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>
          {fill_xml}
          {line_xml}
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square" lIns="{margin * 12700}" tIns="{margin * 12700}" rIns="{margin * 12700}" bIns="{margin * 12700}"/>
          <a:lstStyle/>
          {text_xml}
        </p:txBody>
      </p:sp>"""


def connector(
    sid: int,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    color: str = ACCENT,
    width: int = 15875,
    head_end: str | None = None,
    tail_end: str | None = "triangle",
) -> str:
    flip_h = "1" if x2 < x1 else "0"
    flip_v = "1" if y2 < y1 else "0"
    x_min = min(x1, x2)
    y_min = min(y1, y2)
    cx = max(abs(x2 - x1), 0.01)
    cy = max(abs(y2 - y1), 0.01)
    head_xml = f'<a:headEnd type="{head_end}"/>' if head_end else ""
    tail_xml = f'<a:tailEnd type="{tail_end}"/>' if tail_end else ""
    return f"""
      <p:cxnSp>
        <p:nvCxnSpPr>
          <p:cNvPr id="{sid}" name="Connector {sid}"/>
          <p:cNvCxnSpPr/>
          <p:nvPr/>
        </p:nvCxnSpPr>
        <p:spPr>
          <a:xfrm flipH="{flip_h}" flipV="{flip_v}">
            <a:off x="{inch(x_min)}" y="{inch(y_min)}"/>
            <a:ext cx="{inch(cx)}" cy="{inch(cy)}"/>
          </a:xfrm>
          <a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>
          <a:ln w="{width}" cap="flat">
            <a:solidFill><a:srgbClr val="{color}"/></a:solidFill>
            {head_xml}
            {tail_xml}
          </a:ln>
        </p:spPr>
      </p:cxnSp>"""


def picture(sid: int, x: float, y: float, w: float, h: float, *, name: str, rid: str = "rId2") -> str:
    return f"""
      <p:pic>
        <p:nvPicPr>
          <p:cNvPr id="{sid}" name="{e(name)}"/>
          <p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr>
          <p:nvPr/>
        </p:nvPicPr>
        <p:blipFill>
          <a:blip r:embed="{rid}"/>
          <a:stretch><a:fillRect/></a:stretch>
        </p:blipFill>
        <p:spPr>
          <a:xfrm><a:off x="{inch(x)}" y="{inch(y)}"/><a:ext cx="{inch(w)}" cy="{inch(h)}"/></a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:ln w="12700"><a:solidFill><a:srgbClr val="E3E7EB"/></a:solidFill></a:ln>
        </p:spPr>
      </p:pic>"""


def title(sid: int, text: str, subtitle: str | None = None) -> str:
    parts = [
        shape(sid, 0.65, 0.45, 11.9, 0.72, text, fill="", line="", size=30, bold=True),
    ]
    if subtitle:
        parts.append(shape(sid + 1, 0.68, 1.08, 10.8, 0.35, subtitle, fill="", line="", size=13, text_color=MUTED))
    return "\n".join(parts)


def footer(n: int) -> str:
    return shape(900, 0.65, 7.12, 12.0, 0.22, f"В реальном времени · {n:02d}", fill="", line="", size=8, text_color=MUTED)


def slide_xml(n: int, body: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="{BG}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {body}
      {footer(n)}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>"""


def slide_rels(media_name: str | None = None) -> str:
    media_rel = ""
    if media_name:
        media_rel = (
            f'\n  <Relationship Id="rId2" '
            f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            f'Target="../media/{media_name}"/>'
        )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  {media_rel}
</Relationships>"""


def title_slide(kind: str) -> str:
    if kind == "practice":
        heading = "Презентация по отчёту о прохождении преддипломной практики"
        subtitle = "по теме: «Разработка real-time интерфейса с поддержкой горизонтального масштабирования WebSocket-соединений для системы отслеживания задач»"
        return (
            shape(10, 0.65, 1.0, 11.9, 1.4, heading,
                  fill="", line="", size=24, bold=True, align="ctr")
            + shape(11, 0.65, 2.7, 11.9, 1.6, subtitle,
                    fill="", line="", size=17, text_color=MUTED, align="ctr")
            + shape(12, 0.65, 4.7, 11.9, 0.4, "Студент: Зайцев А. С., группа 4131з",
                    fill="", line="", size=15, align="ctr")
            + shape(13, 0.65, 5.2, 11.9, 0.4, PRACTICE_SUPERVISOR_LINE,
                    fill="", line="", size=15, align="ctr")
            + shape(14, 0.65, 6.0, 11.9, 0.4, "Санкт-Петербург, 2026",
                    fill="", line="", size=14, text_color=MUTED, align="ctr")
        )
    return (
        shape(10, 0.65, 1.45, 11.9, 1.7,
              "Разработка real-time интерфейса с поддержкой горизонтального масштабирования WebSocket-соединений для системы отслеживания задач",
              fill="", line="", size=26, bold=True, align="ctr")
        + shape(11, 0.65, 3.55, 11.9, 0.4, "Защита выпускной квалификационной работы",
                fill="", line="", size=16, text_color=MUTED, align="ctr")
        + shape(12, 0.65, 4.7, 11.9, 0.4, "Студент: Зайцев А. С., группа 4131з",
                fill="", line="", size=15, align="ctr")
        + shape(13, 0.65, 5.2, 11.9, 0.4, VKR_SUPERVISOR_LINE,
                fill="", line="", size=15, align="ctr")
        + shape(14, 0.65, 6.0, 11.9, 0.4, "Санкт-Петербург, 2026",
                fill="", line="", size=14, text_color=MUTED, align="ctr")
    )


def product_image_slide(title_text: str, subtitle: str, image_name: str) -> str:
    return (
        title(10, title_text, subtitle)
        + shape(20, 1.18, 1.48, 10.94, 5.52, "", fill=PANEL, line="D7D2C7", radius=False)
        + picture(21, 1.25, 1.55, 10.8, 5.46, name=image_name)
    )


def sdlc_slide() -> str:
    return (
        title(
            10,
            "Где живёт продукт",
            "У команды есть привычный процесс. Продукт помогает на этапе тестирования.",
        )
        + shape(20, 0.75, 1.95, 2.6, 0.95,
                "Аналитика",
                fill=PANEL, size=15, align="ctr")
        + shape(21, 3.55, 1.95, 2.6, 0.95,
                "Разработка",
                fill=PANEL, size=15, align="ctr")
        + shape(22, 6.35, 1.95, 2.6, 0.95,
                "Тестирование",
                fill=SOFT, line=ACCENT, size=15, bold=True, align="ctr")
        + shape(23, 9.15, 1.95, 2.6, 0.95,
                "Деплой",
                fill=PANEL, size=15, align="ctr")
        + connector(40, 3.35, 2.42, 3.55, 2.42, color=MUTED)
        + connector(41, 6.15, 2.42, 6.35, 2.42, color=MUTED)
        + connector(42, 8.95, 2.42, 9.15, 2.42, color=MUTED)
        + shape(30, 0.75, 3.50, 11.85, 1.55,
                "Продукт — система отслеживания задач и багов.",
                fill="", line="", size=18, bold=True, align="ctr")
        + shape(31, 0.75, 4.30, 11.85, 1.0,
                "В одном отчёте встречаются тестировщик, разработчик и ответственный: "
                "заводят баг, уточняют шаги, меняют статус.",
                fill="", line="", size=15, text_color=MUTED, align="ctr")
        + shape(32, 0.75, 5.55, 11.85, 1.0,
                "Они работают с одним отчётом одновременно — значит, изменения должны быть видны сразу, без перезагрузки страницы.",
                fill=SOFT, line=ACCENT, size=15, bold=True, align="ctr")
    )


def deck_slides(kind: str = "vkr") -> list[str | tuple[str, str]]:
    work_word = "практики" if kind == "practice" else "работы"
    goal_label = "Цель преддипломной практики" if kind == "practice" else "Цель работы"

    # Architecture slide layout — kept in one place so connectors line up with boxes
    cliA = (1.0, 2.05, 1.8, 0.7)
    cliB = (1.0, 4.10, 1.8, 0.7)
    ngx = (3.6, 3.05, 1.5, 0.8)
    api1 = (6.1, 2.05, 2.0, 0.7)
    api2 = (6.1, 4.10, 2.0, 0.7)
    rds = (9.1, 3.05, 2.4, 0.8)

    def right_mid(box):
        x, y, w, h = box
        return x + w, y + h / 2

    def left_mid(box):
        x, y, w, h = box
        return x, y + h / 2

    def left_at(box, dy):
        x, y, w, h = box
        return x, y + h / 2 + dy

    def right_at(box, dy):
        x, y, w, h = box
        return x + w, y + h / 2 + dy

    slides: list[str | tuple[str, str]] = [title_slide(kind)]
    if kind == "vkr":
        slides.extend(
            [
                sdlc_slide(),
                (
                    product_image_slide(
                        "Целевой продукт: дашборд",
                        "Список отчётов команды, статусы, ответственные и активность по задачам (рис. 1 ВКР)",
                        "interface-dashboard.png",
                    ),
                    "interface-dashboard.png",
                ),
                (
                    product_image_slide(
                        "Целевой продукт: страница отчёта",
                        "Основной рабочий экран: отчёт, баги, шаги воспроизведения, комментарии, участники (рис. 2 ВКР)",
                        "interface-report-page.png",
                    ),
                    "interface-report-page.png",
                ),
                # Актуальность — основано на введении ВКР
                title(
                    10,
                    "Почему это актуально сейчас",
                    "Интерфейсы переходят от статичных CRUD-экранов к событийным рабочим пространствам",
                )
                + shape(20, 0.75, 1.75, 11.85, 1.35,
                        "Продукты усложняются\n\n"
                        "Пользователь работает не с одной формой, а с отчётом, багами, статусами и участниками одновременно.",
                        fill=PANEL, size=14)
                + shape(21, 0.75, 3.30, 11.85, 1.35,
                        "AI-инструменты усиливают ожидание обновлений в реальном времени\n\n"
                        "Ассистент может сам создать комментарий, изменить статус, предложить исполнителя.",
                        fill=IRIS_SOFT, line=ACCENT_2, size=14)
                + shape(22, 0.75, 4.85, 11.85, 1.45,
                        "Real-time — это инженерная характеристика, а не «фича»\n\n"
                        "Строить его нужно для нескольких экземпляров серверного сервиса, а не только для одного.",
                        fill=SOFT, line=ACCENT, size=14, bold=True)
                + shape(23, 0.75, 6.45, 11.85, 0.40,
                        "AI-функциональность не утверждается как реализованная — это контекст актуальности.",
                        fill="", line="", size=11, text_color=MUTED, align="ctr"),
            ]
        )

    slides.extend([
        # 5. Проблема — масштабируемость и отказоустойчивость
        title(10, "В чём проблема",
              "Исходный контур реального времени не масштабируется и не отказоустойчив")
        + shape(20, 0.75, 1.55, 5.85, 2.50,
                "Не масштабируется\n\n"
                "Все клиенты обслуживаются одним серверным процессом. "
                "Рост числа пользователей и долгих соединений упирается в один экземпляр; "
                "разгрузить второй сервер нельзя.",
                fill=PANEL, size=14)
        + shape(21, 6.75, 1.55, 5.85, 2.50,
                "Не отказоустойчив\n\n"
                "Этот единственный процесс — единая точка отказа. "
                "При его остановке обновления в реальном времени у всех участников прекращаются, "
                "перезапуск приводит к перерыву в работе.",
                fill=PANEL, size=14)
        + shape(22, 0.75, 4.25, 11.85, 1.55,
                "Если просто запустить второй экземпляр, проблема не решается, а смещается: "
                "событие, созданное на одном узле, не доходит до клиентов, подключённых ко второму. "
                "Совместная работа над отчётом ломается.",
                fill=SOFT, line=ACCENT, size=15, bold=True, align="ctr")
        + shape(23, 0.75, 6.00, 11.85, 0.95,
                "Технически: сведения о подключениях и группах SignalR хранятся в памяти конкретного "
                "серверного процесса, поэтому без межузлового канала общее пространство синхронизации фрагментируется.",
                fill="", line="", size=12, text_color=MUTED, align="ctr"),

        # 6. Цель и задачи — инженерная цель: все слои затронуты
        title(10, f"{goal_label}",
              "Сделать real-time масштабируемым и отказоустойчивым — с доработкой на всех слоях")
        + shape(20, 0.75, 1.65, 11.85, 1.45,
                "Перейти от одноузловой схемы реального времени к распределённому контуру: "
                "несколько экземпляров серверного сервиса обслуживают подключения, "
                "события об изменении сущностей доставляются всем участникам "
                "независимо от узла подключения.",
                fill=SOFT, line=ACCENT, size=15, bold=True, align="ctr")
        + shape(21, 0.75, 3.30, 2.85, 3.30,
                "1. Проектирование\n\n"
                "Архитектура распределённой доставки, поток события и границы решения.",
                fill=PANEL, size=12)
        + shape(22, 3.78, 3.30, 2.85, 3.30,
                "2. Серверная часть\n\n"
                "Диагностика узла, единая точка отправки событий, конфигурируемое подключение общего канала.",
                fill=PANEL, size=12)
        + shape(23, 6.80, 3.30, 2.85, 3.30,
                "3. Клиентская часть\n\n"
                "Восстановление соединения, повторная подписка на отчёт после обрыва, диагностические данные.",
                fill=PANEL, size=12)
        + shape(24, 9.82, 3.30, 2.85, 3.30,
                "4. Инфраструктура и испытания\n\n"
                "Воспроизводимый стенд из двух экземпляров и общей точки входа; программа испытаний и оценка.",
                fill=SOFT, line=ACCENT, size=12, bold=True),

        # Сравнение подходов — табличная форма по §1.4 / таблица ВКР
        title(10, "Сравнение подходов к масштабированию",
              "Шесть рассмотренных вариантов — выбран четвёртый (§1.4, таблица 1.4 ВКР)")
        + shape(80, 0.55, 1.55, 6.40, 0.40, "Подход",
                fill="", line="", size=11, bold=True, text_color=MUTED, margin=8)
        + shape(81, 7.05, 1.55, 1.40, 0.40, "Доставка",
                fill="", line="", size=11, bold=True, text_color=MUTED, align="ctr", margin=4)
        + shape(82, 8.55, 1.55, 4.30, 0.40, "Ограничение",
                fill="", line="", size=11, bold=True, text_color=MUTED, margin=8)
        # 6 строк × (название | бейдж | ограничение)
        + shape(100, 0.55, 2.00, 6.40, 0.70, "1.  Один экземпляр серверного сервиса",
                fill=PANEL, size=12, margin=10)
        + shape(101, 7.05, 2.00, 1.40, 0.70, "Нет",
                fill=DANGER_SOFT, text_color=DANGER, size=12, bold=True, align="ctr", margin=6)
        + shape(102, 8.55, 2.00, 4.30, 0.70, "Только ранний прототип",
                fill=PANEL, size=12, text_color=MUTED, margin=10)
        + shape(110, 0.55, 2.78, 6.40, 0.70, "2.  Несколько экземпляров без общего канала",
                fill=PANEL, size=12, margin=10)
        + shape(111, 7.05, 2.78, 1.40, 0.70, "Нет",
                fill=DANGER_SOFT, text_color=DANGER, size=12, bold=True, align="ctr", margin=6)
        + shape(112, 8.55, 2.78, 4.30, 0.70, "Локальные группы фрагментируются",
                fill=PANEL, size=12, text_color=MUTED, margin=10)
        + shape(120, 0.55, 3.56, 6.40, 0.70, "3.  Закрепление клиента за узлом",
                fill=PANEL, size=12, margin=10)
        + shape(121, 7.05, 3.56, 1.40, 0.70, "Нет",
                fill=DANGER_SOFT, text_color=DANGER, size=12, bold=True, align="ctr", margin=6)
        + shape(122, 8.55, 3.56, 4.30, 0.70, "Не доставляет события другим узлам",
                fill=PANEL, size=12, text_color=MUTED, margin=10)
        + shape(130, 0.55, 4.34, 6.40, 0.80, "4.  Redis backplane для SignalR — выбрано",
                fill=SOFT, line=ACCENT, size=12, bold=True, margin=10)
        + shape(131, 7.05, 4.34, 1.40, 0.80, "Да",
                fill=SOFT, line=ACCENT, text_color=ACCENT, size=12, bold=True, align="ctr", margin=6)
        + shape(132, 8.55, 4.34, 4.30, 0.80, "Сохраняет SignalR-группы, локальный стенд",
                fill=SOFT, line=ACCENT, size=12, bold=True, margin=10)
        + shape(140, 0.55, 5.22, 6.40, 0.70, "5.  Брокер сообщений или шина событий",
                fill=PANEL, size=12, margin=10)
        + shape(141, 7.05, 5.22, 1.40, 0.70, "Да",
                fill=PANEL, text_color=ACCENT, size=12, bold=True, align="ctr", margin=6)
        + shape(142, 8.55, 5.22, 4.30, 0.70, "Требует переработки доменных событий",
                fill=PANEL, size=12, text_color=MUTED, margin=10)
        + shape(150, 0.55, 6.00, 6.40, 0.70, "6.  Управляемый облачный сервис реального времени",
                fill=PANEL, size=12, margin=10)
        + shape(151, 7.05, 6.00, 1.40, 0.70, "Да",
                fill=PANEL, text_color=ACCENT, size=12, bold=True, align="ctr", margin=6)
        + shape(152, 8.55, 6.00, 4.30, 0.70, "Снижает контроль над локальным контуром",
                fill=PANEL, size=12, text_color=MUTED, margin=10)
        + shape(160, 0.55, 6.78, 12.30, 0.30,
                "Критерии: межузловая доставка · сохранение модели групп SignalR · self-hosted · "
                "без переработки доменных событий · воспроизводимость в Docker Compose",
                fill="", line="", size=10, text_color=MUTED, align="ctr"),

        # 8. Целевая архитектура
        title(10, "Как это устроено",
              "Два экземпляра backend за общей точкой входа · общий канал событий через Redis")
        + shape(20, *cliA, "Клиент A", fill=PANEL, size=14, bold=True, align="ctr")
        + shape(21, *cliB, "Клиент B", fill=PANEL, size=14, bold=True, align="ctr")
        + shape(22, *ngx, "nginx", fill=SOFT, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(23, *api1, "app-api-1", fill=PANEL, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(24, *api2, "app-api-2", fill=PANEL, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(25, *rds, "Общий канал (Redis)", fill=IRIS_SOFT, line=ACCENT_2, size=14, bold=True, align="ctr")
        + connector(50, *right_mid(cliA), *left_at(ngx, -0.18))
        + connector(51, *right_mid(cliB), *left_at(ngx, +0.18))
        + connector(52, *right_at(ngx, -0.18), *left_mid(api1))
        + connector(53, *right_at(ngx, +0.18), *left_mid(api2))
        + connector(54, *right_mid(api1), *left_at(rds, -0.18),
                    color=ACCENT_2, head_end="triangle", tail_end="triangle")
        + connector(55, *right_mid(api2), *left_at(rds, +0.18),
                    color=ACCENT_2, head_end="triangle", tail_end="triangle")
        + shape(26, 0.7, 5.4, 12.0, 0.5,
                "Событие уходит в Redis и приходит на оба экземпляра. Оттуда — клиентам, которые сейчас открыли отчёт.",
                fill="", line="", size=13, text_color=MUTED, align="ctr")
        + shape(27, 0.7, 5.95, 12.0, 0.4,
                "База данных у экземпляров общая — здесь она опущена, чтобы не отвлекать от канала доставки.",
                fill="", line="", size=11, text_color=MUTED, align="ctr"),

        # Поток события — §3.3 ВКР, рис. 6 (sequence)
        title(10, "Что происходит при изменении отчёта",
              "Шесть шагов от действия пользователя до клиента на другом узле (§3.3, рис. 6 ВКР)")
        + shape(20, 0.55, 1.95, 1.95, 4.20,
                "1. Действие пользователя\n\n"
                "Клиент A меняет заголовок отчёта.",
                fill=PANEL, size=12)
        + shape(21, 2.65, 1.95, 1.95, 4.20,
                "2. HTTP-запрос\n\n"
                "Через общую точку входа запрос попадает на один из узлов — узел 1.",
                fill=PANEL, size=12)
        + shape(22, 4.75, 1.95, 1.95, 4.20,
                "3. Сохранение в базе\n\n"
                "Изменение фиксируется в PostgreSQL — это источник истины.",
                fill=PANEL, size=12)
        + shape(23, 6.85, 1.95, 1.95, 4.20,
                "4. Публикация события\n\n"
                "Сервис формирует событие изменения отчёта и отправляет его в группу.",
                fill=SOFT, line=ACCENT, size=12, bold=True)
        + shape(24, 8.95, 1.95, 1.95, 4.20,
                "5. Межузловая доставка\n\n"
                "Через общий канал событие становится доступным узлу 2.",
                fill=IRIS_SOFT, line=ACCENT_2, size=12, bold=True)
        + shape(25, 11.05, 1.95, 1.95, 4.20,
                "6. Клиент B получает\n\n"
                "Клиент на другом узле получает то же событие.",
                fill=SOFT, line=ACCENT, size=12, bold=True)
        + shape(26, 0.55, 6.40, 12.45, 0.45,
                "REST остаётся источником команд и состояния, real-time — каналом распространения изменений.",
                fill="", line="", size=12, text_color=MUTED, align="ctr"),

        # Программная реализация — пять направлений работ по §4.1 ВКР
        title(10, "Программная реализация",
              "Пять направлений работ (§4.1 ВКР)")
        + shape(20, 0.55, 1.80, 2.40, 4.50,
                "1. Серверная конфигурация\n\n"
                "Включаемое через переменную окружения подключение общего канала событий.",
                fill=PANEL, size=13)
        + shape(21, 3.00, 1.80, 2.40, 4.50,
                "2. Хаб и отправка событий\n\n"
                "Идентификатор узла, единая точка отправки, диагностика подключения.",
                fill=PANEL, size=13)
        + shape(22, 5.45, 1.80, 2.40, 4.50,
                "3. Клиентская часть\n\n"
                "Автоматическое переподключение и повторная подписка на текущий отчёт.",
                fill=PANEL, size=13)
        + shape(23, 7.90, 1.80, 2.40, 4.50,
                "4. Инфраструктура стенда\n\n"
                "Два экземпляра серверного сервиса, общая точка входа, общая база и общий канал.",
                fill=SOFT, line=ACCENT, size=13, bold=True)
        + shape(24, 10.35, 1.80, 2.40, 4.50,
                "5. Проверочный клиент\n\n"
                "Отдельный скрипт, который подключается к двум узлам и измеряет задержку доставки.",
                fill=IRIS_SOFT, line=ACCENT_2, size=13, bold=True)
        + shape(25, 0.55, 6.55, 12.30, 0.35,
                "Стек: ASP.NET Core, SignalR, Redis, React, TypeScript, Node.js, nginx, Docker Compose",
                fill="", line="", size=11, text_color=MUTED, align="ctr"),

        # Стенд испытаний — §4.5 ВКР, без команд запуска
        title(10, "Стенд испытаний",
              "Воспроизводимое локальное окружение из шести компонентов (§4.5 ВКР)")
        + shape(20, 4.10, 1.65, 5.10, 1.10,
                "Проверочный клиент",
                fill=IRIS_SOFT, line=ACCENT_2, size=14, bold=True, align="ctr")
        + shape(21, 4.10, 2.95, 5.10, 1.10,
                "Общая точка входа (nginx)",
                fill=SOFT, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(22, 0.95, 4.25, 4.20, 1.10,
                "Серверный сервис №1",
                fill=PANEL, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(23, 8.15, 4.25, 4.20, 1.10,
                "Серверный сервис №2",
                fill=PANEL, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(24, 0.95, 5.55, 4.20, 1.10,
                "Общая база (PostgreSQL)",
                fill=PANEL, size=13, align="ctr")
        + shape(25, 8.15, 5.55, 4.20, 1.10,
                "Общий канал событий (Redis)",
                fill=IRIS_SOFT, line=ACCENT_2, size=13, bold=True, align="ctr")
        + connector(70, 6.65, 2.75, 6.65, 2.95, color=MUTED)
        + connector(71, 5.50, 4.05, 3.05, 4.25, color=MUTED)
        + connector(72, 7.85, 4.05, 10.25, 4.25, color=MUTED)
        + connector(73, 3.05, 5.35, 3.05, 5.55, color=MUTED)
        + connector(74, 10.25, 5.35, 10.25, 5.55, color=ACCENT_2)
        + connector(76, 4.55, 5.35, 8.55, 5.55, color=ACCENT_2)
        + connector(77, 8.75, 5.35, 4.55, 5.55, color=MUTED)
        + shape(26, 0.55, 6.85, 12.30, 0.30,
                "Оба сервиса собраны из одного образа и отличаются только идентификатором экземпляра.",
                fill="", line="", size=11, text_color=MUTED, align="ctr"),

        # Программа испытаний — §5.1 ВКР
        title(10, "Программа испытаний",
              "Один и тот же стенд, два режима, пять проверок (§5.1 ВКР)")
        + shape(20, 0.75, 1.65, 5.85, 4.95,
                "Два режима одного стенда\n\n"
                "•  Без общего канала событий — контрольный режим, "
                "воспроизводит исходное ограничение.\n\n"
                "•  С общим каналом событий — целевой режим, проверяет решение.\n\n"
                "Код и сценарий — одни и те же. Меняется только одна настройка: "
                "включён общий канал или нет.",
                fill=PANEL, size=14)
        + shape(21, 6.75, 1.65, 5.85, 4.95,
                "Пять проверок\n\n"
                "1.  Одиночная доставка без общего канала.\n\n"
                "2.  Одиночная доставка с общим каналом.\n\n"
                "3.  Серия из 30 повторов — повторяемость и задержка.\n\n"
                "4.  Восстановление подписки после разрыва соединения.\n\n"
                "5.  Переключение на другой узел после отказа.",
                fill=SOFT, line=ACCENT, size=14, bold=True),

        # 11. Главный результат — без / с
        title(10, "Главный результат",
              "Один и тот же сценарий, разница — только в общем канале")
        + shape(20, 0.75, 1.7, 5.85, 3.6,
                "Без общего канала\n\n"
                "Событие так и не пришло.\n\n"
                "Клиент ждал 10 секунд — ничего.",
                fill=DANGER_SOFT, line=DANGER, text_color=DANGER, size=20, bold=True, align="ctr")
        + shape(21, 6.75, 1.7, 5.85, 3.6,
                "С общим каналом\n\n"
                "Событие пришло.\n\n"
                "От момента отправки до клиента — около 9,5 мс.",
                fill=SOFT, line=ACCENT, size=20, bold=True, align="ctr")
        + shape(22, 0.75, 5.55, 11.85, 0.85,
                "Изменился ровно один параметр — поведение изменилось ровно так, как ожидалось. "
                "Это и подтверждает, что причина именно в общем канале.",
                fill="", line="", size=13, text_color=MUTED, align="ctr"),

        # Расширенные сценарии — §5.5–5.6 ВКР
        title(10, "Расширенные сценарии испытаний",
              "Повторяемость задержки и устойчивость к разрывам и отказам (§5.5–5.6 ВКР)")
        + shape(20, 0.75, 1.75, 4.0, 4.65,
                "Серийная проверка (§5.5)\n\n"
                "30 повторов подряд в целевом режиме.\n\n"
                "Успешно: 30 из 30\n"
                "среднее 7,2 мс  ·  медиана 6,1 мс\n"
                "минимум 3,8 мс  ·  95 % быстрее 13,8 мс\n\n"
                "Повторяемость доставки и порядок задержки на локальном стенде.",
                fill=PANEL, size=13)
        + shape(21, 4.85, 1.75, 4.0, 4.65,
                "Повторная подписка (§5.6)\n\n"
                "Разрыв соединения, новое подключение, повторное вступление в группу отчёта.\n\n"
                "переподключение 6,5 мс\n"
                "доставка после восстановления 15,2 мс\n\n"
                "Контур устойчив к разрыву клиентского соединения.",
                fill=PANEL, size=13)
        + shape(22, 8.95, 1.75, 4.0, 4.65,
                "Переключение после отказа (§5.6)\n\n"
                "Остановка одного из узлов, переключение через общую точку входа на оставшийся.\n\n"
                "переключение 352 мс\n"
                "доставка после переключения 5,4 мс\n\n"
                "Контур устойчив к отказу одного узла.",
                fill=PANEL, size=13),

        # Сводка результатов — таблица 5.7 ВКР
        title(10, "Сводка результатов",
              "Сопоставление режимов и сценариев (таблица 5.7 ВКР)")
        + shape(80, 0.55, 1.55, 4.85, 0.40, "Сценарий",
                fill="", line="", size=11, bold=True, text_color=MUTED, margin=8)
        + shape(81, 5.50, 1.55, 1.10, 0.40, "Общий канал",
                fill="", line="", size=11, bold=True, text_color=MUTED, align="ctr", margin=4)
        + shape(82, 6.70, 1.55, 3.75, 0.40, "Фактический результат",
                fill="", line="", size=11, bold=True, text_color=MUTED, margin=8)
        + shape(83, 10.55, 1.55, 2.30, 0.40, "Вывод",
                fill="", line="", size=11, bold=True, text_color=MUTED, margin=8)
        + shape(200, 0.55, 2.00, 4.85, 0.75, "Доставка без общего канала",
                fill=PANEL, size=12, margin=10)
        + shape(201, 5.50, 2.00, 1.10, 0.75, "Нет",
                fill=DANGER_SOFT, text_color=DANGER, size=12, bold=True, align="ctr", margin=6)
        + shape(202, 6.70, 2.00, 3.75, 0.75, "Тайм-аут 10 000 мс",
                fill=PANEL, size=12, margin=10)
        + shape(203, 10.55, 2.00, 2.30, 0.75, "Ограничение воспроизведено",
                fill=DANGER_SOFT, text_color=DANGER, size=11, bold=True, align="ctr", margin=8)
        + shape(210, 0.55, 2.80, 4.85, 0.75, "Доставка с общим каналом",
                fill=PANEL, size=12, margin=10)
        + shape(211, 5.50, 2.80, 1.10, 0.75, "Да",
                fill=SOFT, line=ACCENT, text_color=ACCENT, size=12, bold=True, align="ctr", margin=6)
        + shape(212, 6.70, 2.80, 3.75, 0.75, "Событие доставлено · задержка ≈ 9,5 мс",
                fill=PANEL, size=12, margin=10)
        + shape(213, 10.55, 2.80, 2.30, 0.75, "Ограничение устранено",
                fill=SOFT, line=ACCENT, text_color=ACCENT, size=11, bold=True, align="ctr", margin=8)
        + shape(220, 0.55, 3.60, 4.85, 0.75, "Серия из 30 итераций",
                fill=PANEL, size=12, margin=10)
        + shape(221, 5.50, 3.60, 1.10, 0.75, "Да",
                fill=PANEL, text_color=ACCENT, size=12, bold=True, align="ctr", margin=6)
        + shape(222, 6.70, 3.60, 3.75, 0.75, "30 из 30 · 95 % быстрее 13,8 мс",
                fill=PANEL, size=12, margin=10)
        + shape(223, 10.55, 3.60, 2.30, 0.75, "Повторяемость подтверждена",
                fill=PANEL, text_color=ACCENT, size=11, bold=True, align="ctr", margin=8)
        + shape(230, 0.55, 4.40, 4.85, 0.75, "Повторная подписка после разрыва",
                fill=PANEL, size=12, margin=10)
        + shape(231, 5.50, 4.40, 1.10, 0.75, "Да",
                fill=PANEL, text_color=ACCENT, size=12, bold=True, align="ctr", margin=6)
        + shape(232, 6.70, 4.40, 3.75, 0.75, "Событие после восстановления · 15,2 мс",
                fill=PANEL, size=12, margin=10)
        + shape(233, 10.55, 4.40, 2.30, 0.75, "Подписка восстановлена",
                fill=PANEL, text_color=ACCENT, size=11, bold=True, align="ctr", margin=8)
        + shape(240, 0.55, 5.20, 4.85, 0.75, "Переключение после отказа узла",
                fill=PANEL, size=12, margin=10)
        + shape(241, 5.50, 5.20, 1.10, 0.75, "Да",
                fill=PANEL, text_color=ACCENT, size=12, bold=True, align="ctr", margin=6)
        + shape(242, 6.70, 5.20, 3.75, 0.75, "Узел 2 → узел 1, событие получено",
                fill=PANEL, size=12, margin=10)
        + shape(243, 10.55, 5.20, 2.30, 0.75, "Восстановление после отказа",
                fill=PANEL, text_color=ACCENT, size=11, bold=True, align="ctr", margin=8)
        + shape(250, 0.55, 6.20, 12.30, 0.65,
                "Сопоставление режимов на одном стенде с одним кодом показывает причинную связь "
                "между включением межузлового канала и доставкой события.",
                fill="", line="", size=12, text_color=MUTED, align="ctr"),

        # 13. Ограничения
        title(10, "Чего решение не делает",
              "Это интерфейсная синхронизация, а не строгий промышленный режим реального времени")
        + shape(20, 0.75, 1.65, 3.85, 4.75,
                "Задержка не нулевая\n\n"
                "Событие проходит через два экземпляра и общий канал.\n\n"
                "На стенде получилось ~7 мс в среднем.",
                fill=PANEL, size=14)
        + shape(21, 4.80, 1.65, 3.85, 4.75,
                "Источник истины — база\n\n"
                "Если возникает сомнение в состоянии, клиент всегда может перечитать "
                "его обычным HTTP-запросом.",
                fill=PANEL, size=14)
        + shape(22, 8.85, 1.65, 3.85, 4.75,
                "Что было бы дальше\n\n"
                "Прочный журнал событий, версии сущностей, гарантии доставки — "
                "если потребуется строгая согласованность между сервисами.",
                fill=IRIS_SOFT, line=ACCENT_2, size=14, bold=True),

        # 14. Вывод
        title(10, "Итог")
        + shape(20, 0.75, 1.75, 11.85, 1.35,
                f"Изменения в отчёте теперь доходят до всех участников — "
                f"независимо от того, к какому экземпляру backend они подключены.",
                fill=SOFT, line=ACCENT, size=18, bold=True, align="ctr")
        + shape(21, 0.75, 3.30, 11.85, 1.3,
                "Дополнительный эффект — при падении одного экземпляра пользователи продолжают работать через другой.",
                fill=IRIS_SOFT, line=ACCENT_2, size=14, align="ctr")
        + shape(22, 0.75, 4.95, 3.85, 1.85,
                "Что было\n\n"
                "С несколькими экземплярами backend изменения не доходили до части пользователей.",
                fill=PANEL, size=13)
        + shape(23, 4.75, 4.95, 3.85, 1.85,
                "Что сделали\n\n"
                "Два экземпляра за общей точкой входа плюс общий канал событий через Redis.",
                fill=PANEL, size=13)
        + shape(24, 8.75, 4.95, 3.85, 1.85,
                "Чем доказали\n\n"
                "Сравнение «без / с», 30 повторов, переподключение и падение узла.",
                fill=PANEL, size=13),
    ])
    return slides


def content_types(slide_count: int) -> str:
    overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  {overrides}
</Types>"""


def presentation_xml(slide_count: int) -> str:
    slide_ids = "\n".join(
        f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""


def presentation_rels(slide_count: int) -> str:
    rels = ['<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    for i in range(1, slide_count + 1):
        rels.append(f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {' '.join(rels)}
</Relationships>"""


def static_parts() -> dict[str, str]:
    return {
        "_rels/.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>""",
        "docProps/core.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>ВКР real-time scale-out</dc:title><dc:creator>Codex</dc:creator>
</cp:coreProperties>""",
        "docProps/app.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Codex</Application></Properties>""",
        "ppt/slideMasters/slideMaster1.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>""",
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>""",
        "ppt/slideLayouts/slideLayout1.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
</p:sldLayout>""",
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>""",
        "ppt/theme/theme1.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="VKR">
  <a:themeElements><a:clrScheme name="VKR"><a:dk1><a:srgbClr val="18212B"/></a:dk1><a:lt1><a:srgbClr val="F6F3EC"/></a:lt1><a:dk2><a:srgbClr val="293241"/></a:dk2><a:lt2><a:srgbClr val="FFFFFF"/></a:lt2><a:accent1><a:srgbClr val="0B6E69"/></a:accent1><a:accent2><a:srgbClr val="C76F2E"/></a:accent2><a:accent3><a:srgbClr val="E8F3F1"/></a:accent3><a:accent4><a:srgbClr val="FFF3D8"/></a:accent4><a:accent5><a:srgbClr val="5E6A75"/></a:accent5><a:accent6><a:srgbClr val="E3E7EB"/></a:accent6><a:hlink><a:srgbClr val="0B6E69"/></a:hlink><a:folHlink><a:srgbClr val="0B6E69"/></a:folHlink></a:clrScheme><a:fontScheme name="Verdana"><a:majorFont><a:latin typeface="Verdana"/></a:majorFont><a:minorFont><a:latin typeface="Verdana"/></a:minorFont></a:fontScheme><a:fmtScheme name="VKR"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements>
</a:theme>""",
    }


def build(kind: str = "vkr") -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slides = deck_slides(kind)
    out_path = PRACTICE_OUT_PPTX if kind == "practice" else OUT_PPTX
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(slides)))
        z.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        for path, content in static_parts().items():
            z.writestr(path, content)
        written_media: set[str] = set()
        for i, slide in enumerate(slides, start=1):
            if isinstance(slide, tuple):
                body, media_name = slide
            else:
                body, media_name = slide, None
            z.writestr(f"ppt/slides/slide{i}.xml", slide_xml(i, body))
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels(media_name))
            if media_name and media_name not in written_media:
                z.write(MEDIA_IMAGES[media_name], f"ppt/media/{media_name}")
                written_media.add(media_name)
    return out_path


def main(kind: str | None = None):
    selected = kind or ("practice" if "--practice" in sys.argv else "vkr")
    if selected not in {"vkr", "practice"}:
        raise ValueError(f"Unknown deck kind: {selected}")
    print(build(selected))


if __name__ == "__main__":
    main()
