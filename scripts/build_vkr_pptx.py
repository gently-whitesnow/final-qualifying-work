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

BG = "F6F3EC"
INK = "18212B"
MUTED = "5E6A75"
ACCENT = "0B6E69"
ACCENT_2 = "C76F2E"
PANEL = "FFFFFF"
SOFT = "E8F3F1"
WARN = "FFF3D8"
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
                  <a:latin typeface="Aptos"/>
                  <a:cs typeface="Aptos"/>
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
    line: str = "D7D2C7",
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
          <a:ln w="12700"><a:solidFill><a:srgbClr val="D7D2C7"/></a:solidFill></a:ln>
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
    return shape(900, 0.65, 7.12, 12.0, 0.22, f"Real-time scale-out · {n:02d}", fill="", line="", size=8, text_color=MUTED)


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
                (
                    product_image_slide(
                        "Целевой продукт: дашборд",
                        "Пользователь видит отчёты команды, статусы, ответственных и активность по задачам",
                        "interface-dashboard.png",
                    ),
                    "interface-dashboard.png",
                ),
                (
                    product_image_slide(
                        "Целевой продукт: страница отчёта",
                        "Основной рабочий экран: отчёт, баги, шаги воспроизведения, комментарии и участники",
                        "interface-report-page.png",
                    ),
                    "interface-report-page.png",
                ),
            ]
        )

    slides.extend([
        # Проблема и цель работы
        title(10, "Проблема и цель", "Single-node SignalR ограничивает горизонтальное масштабирование")
        + shape(20, 0.75, 1.65, 5.85, 4.6,
                "Проблема\n\n"
                "Сведения о подключениях и группах SignalR хранятся в памяти процесса.\n\n"
                "При нескольких экземплярах backend событие, созданное на одном узле, "
                "не доходит до клиента, подключенного к другому узлу.\n\n"
                "Real-time пространство фрагментируется на независимые острова.",
                fill=PANEL, size=16)
        + shape(21, 6.75, 1.65, 5.85, 4.6,
                f"{goal_label}\n\n"
                "Real-time интерфейс системы отслеживания задач, "
                "в котором WebSocket-соединения обслуживаются несколькими экземплярами app-api, "
                "а события об изменении сущностей доставляются клиентам "
                "независимо от узла подключения.",
                fill=SOFT, line=ACCENT, size=16, bold=True),

        # 3. Современный контекст
        title(10, "Современный контекст",
              "Интерфейсы становятся событийными; AI-инструменты усиливают ожидание живой синхронизации")
        + shape(20, 0.75, 1.65, 3.85, 4.75,
                "Рост сложности продуктов\n\n"
                "Пользователь работает не с одной формой, а с отчётом, багами, комментариями, вложениями, статусами и участниками.\n\n"
                "Изменения должны становиться видимыми без ручного обновления страницы.",
                fill=PANEL, size=14)
        + shape(21, 4.8, 1.65, 3.85, 4.75,
                "AI-ready сценарии\n\n"
                "Фоновый сервис или ассистент может предложить исполнителя, дополнить описание, создать комментарий или изменить статус.\n\n"
                "В ВКР это контекст актуальности, а не заявление о готовой AI-функции.",
                fill=WARN, line=ACCENT_2, size=14)
        + shape(22, 8.85, 1.65, 3.85, 4.75,
                "REST + real-time\n\n"
                "HTTP-запрос фиксирует изменение состояния.\n\n"
                "SignalR-событие распространяет изменение активным участникам, включая клиентов на других backend-узлах.",
                fill=SOFT, line=ACCENT, size=14, bold=True),

        # 4. Предметная область
        title(10, "Предметная область",
              "Real-time связан с сущностями продукта, а не с абстрактным WebSocket-демо")
        + shape(20, 0.75, 1.65, 12.0, 0.75,
                "Система отслеживания задач: отчёты · баги · комментарии · вложения · ссылки · шаги воспроизведения · статусы",
                fill=SOFT, line=ACCENT, size=16, bold=True, align="ctr")
        + shape(21, 0.75, 2.7, 3.85, 3.2,
                "Открытие отчёта\n\nJoinReportGroupAsync\n\n"
                "Клиент вступает в группу отчёта и получает только релевантные события.",
                fill=PANEL, size=14, bold=True)
        + shape(22, 4.8, 2.7, 3.85, 3.2,
                "Изменение сущностей\n\nReceiveReportPatch\nReceiveBugCreate\nReceiveCommentUpdate\n\n"
                "События применяются к состоянию интерфейса.",
                fill=PANEL, size=14, bold=True)
        + shape(23, 8.85, 2.7, 3.85, 3.2,
                "Восстановление\n\nonreconnected\nJoinReportGroupAsync\n\n"
                "После reconnect клиент повторно восстанавливает подписку на текущий отчёт.",
                fill=PANEL, size=14, bold=True),

        # 5. Анализ подходов к масштабированию
        title(10, "Анализ подходов к масштабированию",
              "Шесть рассмотренных вариантов; для реализации выбран подход 4")
        + shape(20, 0.75, 1.7, 4.0, 1.45,
                "Один экземпляр backend\nНет масштабирования; один узел — единственная точка отказа",
                fill=PANEL, size=13)
        + shape(21, 4.85, 1.7, 4.0, 1.45,
                "Несколько экземпляров без общего канала\nСобытия не доходят до клиентов, подключённых к другим узлам",
                fill=PANEL, size=13)
        + shape(22, 8.95, 1.7, 4.0, 1.45,
                "Привязка клиента к узлу (sticky)\nКлиент остаётся на одном узле, но события на другие не приходят",
                fill=PANEL, size=13)
        + shape(23, 0.75, 3.30, 4.0, 1.45,
                "Внешняя шина событий\nДоставка между узлами есть, но требуется отдельная схема событий",
                fill=PANEL, size=13)
        + shape(24, 4.85, 3.30, 4.0, 1.45,
                "Облачный real-time сервис\nГотовое решение, но снижает контроль над собственным контуром",
                fill=PANEL, size=13)
        + shape(25, 8.95, 3.30, 4.0, 1.45,
                "Redis backplane для SignalR — выбрано\nШтатный механизм, без перестройки кода, подходит для событий интерфейса",
                fill=SOFT, line=ACCENT, size=13, bold=True)
        + shape(26, 0.75, 5.05, 12.2, 1.4,
                "Критерии выбора: запускается на локальном стенде, "
                "сохраняет существующий код доставки событий, штатно поддерживается в ASP.NET Core SignalR, "
                "подходит для коротких событий интерфейса и легко воспроизводится.",
                fill="", line="", size=12, text_color=MUTED),

        # 6. Целевая архитектура (со стрелками)
        title(10, "Целевая архитектура",
              "Два экземпляра app-api за nginx, общий Redis backplane для межузловой доставки")
        + shape(20, *cliA, "Клиент A", fill=PANEL, size=14, bold=True, align="ctr")
        + shape(21, *cliB, "Клиент B", fill=PANEL, size=14, bold=True, align="ctr")
        + shape(22, *ngx, "nginx", fill=SOFT, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(23, *api1, "app-api-1", fill=PANEL, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(24, *api2, "app-api-2", fill=PANEL, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(25, *rds, "Redis backplane", fill=SOFT, line=ACCENT, size=14, bold=True, align="ctr")
        # connectors
        + connector(50, *right_mid(cliA), *left_at(ngx, -0.18))
        + connector(51, *right_mid(cliB), *left_at(ngx, +0.18))
        + connector(52, *right_at(ngx, -0.18), *left_mid(api1))
        + connector(53, *right_at(ngx, +0.18), *left_mid(api2))
        + connector(54, *right_mid(api1), *left_at(rds, -0.18),
                    head_end="triangle", tail_end="triangle")
        + connector(55, *right_mid(api2), *left_at(rds, +0.18),
                    head_end="triangle", tail_end="triangle")
        + shape(26, 0.7, 5.4, 12.0, 0.5,
                "Событие публикуется в Redis · доставляется обоим узлам · группы SignalR остаются локальным runtime-состоянием",
                fill="", line="", size=13, text_color=MUTED, align="ctr")
        + shape(27, 0.7, 5.95, 12.0, 0.4,
                "Оба экземпляра подключены к общей PostgreSQL; на схеме показан только канал real-time-доставки.",
                fill="", line="", size=11, text_color=MUTED, align="ctr"),

        # 7. Программная реализация
        title(10, "Программная реализация",
              "Backend, frontend, тесты и проверочный клиент закрывают задачу как разработку ПО")
        + shape(20, 0.75, 1.65, 5.85, 2.0,
                "Backend\n\n"
                "AddStackExchangeRedis через REDIS_CONNECTION_STRING\n"
                "GetConnectionDiagnosticsAsync\n"
                "SendToGroupAsync с eventId и GroupExcept",
                fill=PANEL, size=14)
        + shape(21, 6.75, 1.65, 5.85, 2.0,
                "Frontend\n\n"
                "WebSocket transport\n"
                "automatic reconnect\n"
                "повторный JoinReportGroupAsync после reconnect",
                fill=PANEL, size=14)
        + shape(22, 0.75, 4.05, 5.85, 2.1,
                "Тесты\n\n"
                "reconnectJoinHandler проверяет отсутствие лишнего join, "
                "повторное вступление и использование актуального reportId.",
                fill=SOFT, line=ACCENT, size=14, bold=True)
        + shape(23, 6.75, 4.05, 5.85, 2.1,
                "Проверочный клиент\n\n"
                "delivery · rejoin · failover · series\n"
                "Фиксирует serverInstanceId, connectionId, событие и задержку.",
                fill=SOFT, line=ACCENT, size=14, bold=True),

        # 8. Программа испытаний
        title(10, "Программа испытаний",
              "Два режима по одному коду · четыре сценария проверки")
        + shape(20, 0.75, 1.7, 5.85, 4.55,
                "Два режима\n\n"
                "• Без межузлового канала — воспроизведение проблемы\n\n"
                "• С межузловым каналом — проверка решения\n\n"
                "Один и тот же код, один и тот же сценарий; "
                "отличие — наличие Redis backplane.",
                fill=PANEL, size=15)
        + shape(21, 6.75, 1.7, 5.85, 4.55,
                "Четыре сценария\n\n"
                "• Одиночная доставка между узлами\n\n"
                "• Серия из 30 итераций\n\n"
                "• Восстановление подписки после разрыва\n\n"
                "• Переключение на другой узел после отказа",
                fill=PANEL, size=15),

        # 9. Главный результат — без / с backplane
        title(10, "Главный результат",
              "Один код и один сценарий — разница только в наличии Redis-канала")
        + shape(20, 0.75, 1.7, 5.85, 3.6,
                "Без backplane\n\n"
                "ReceiveReportPatch\ntimed out · 10 000 мс\n\n"
                "Событие, созданное на app-api-1, не дошло до клиента на app-api-2",
                fill=WARN, line=ACCENT_2, size=18, bold=True, align="ctr")
        + shape(21, 6.75, 1.7, 5.85, 3.6,
                "С backplane\n\n"
                "ok: true · ReceiveReportPatch получен\n"
                "deliveryLatencyMs ≈ 9,5 мс\n\n"
                "Клиент на app-api-2 получил событие с app-api-1",
                fill=SOFT, line=ACCENT, size=18, bold=True, align="ctr")
        + shape(22, 0.75, 5.55, 11.85, 0.85,
                "Сопоставление двух режимов на одном стенде показывает причинную связь "
                "между включением межузлового канала SignalR и успешной доставкой события.",
                fill="", line="", size=13, text_color=MUTED, align="ctr"),

        # 10. Дополнительные проверки: серия, rejoin, failover
        title(10, "Дополнительные проверки",
              "Повторяемость, восстановление подписки и переключение после отказа узла")
        + shape(20, 0.75, 1.75, 4.0, 4.5,
                "Серия из 30 итераций\n\n"
                "Успешно: 30 из 30\n\n"
                "min 3,8 мс\navg 7,2 мс\np50 6,1 мс\np95 13,8 мс\n\n"
                "Подтверждена повторяемость доставки.",
                fill=PANEL, size=15)
        + shape(21, 4.85, 1.75, 4.0, 4.5,
                "Восстановление подписки\n\n"
                "После разрыва клиент создаёт новое соединение и снова вступает в группу отчёта.\n\n"
                "переподключение 6,5 мс\nдоставка 15,2 мс\n\n"
                "Подтверждена повторная подписка.",
                fill=PANEL, size=15)
        + shape(22, 8.95, 1.75, 4.0, 4.5,
                "Переключение после отказа узла\n\n"
                "Один backend остановлен; nginx переключает клиента на другой экземпляр.\n\n"
                "переподключение 352,0 мс\nдоставка 5,4 мс\n\n"
                "Подтверждено восстановление после отказа.",
                fill=PANEL, size=15),

        # 11. Ограничения
        title(10, "Ограничения",
              "Решение предназначено для интерфейсной синхронизации, а не для жёсткого real-time")
        + shape(20, 0.75, 1.65, 3.85, 4.75,
                "Ненулевая задержка\n\n"
                "Событие проходит через app-api, Redis backplane и другой app-api.\n\n"
                "В локальной серии: avg 7,2 мс, p95 13,8 мс.",
                fill=PANEL, size=14)
        + shape(21, 4.8, 1.65, 3.85, 4.75,
                "Transient UI-events\n\n"
                "Источник истины — PostgreSQL.\n\n"
                "При сомнениях клиент восстанавливает согласованность повторным HTTP-запросом состояния.",
                fill=PANEL, size=14)
        + shape(22, 8.85, 1.65, 3.85, 4.75,
                "Дальнейшее развитие\n\n"
                "Durable broker/event log\n"
                "версии сущностей\n"
                "optimistic concurrency\n"
                "outbox/inbox\n"
                "повторная синхронизация по версии",
                fill=WARN, line=ACCENT_2, size=14, bold=True),

        # 12. Вывод
        title(10, "Вывод")
        + shape(20, 0.75, 1.7, 11.85, 1.4,
                f"Ограничение single-node WebSocket-архитектуры устранено за счёт распределённого real-time контура; "
                f"тезис {work_word} подтверждён экспериментально.",
                fill=SOFT, line=ACCENT, size=17, bold=True, align="ctr")
        + shape(21, 0.75, 3.25, 11.85, 1.55,
                "Дополнительный эффект — повышение отказоустойчивости: "
                "при отказе одного узла клиенты продолжают получать события "
                "через другой экземпляр backend, тогда как single-node архитектура "
                "такой возможности не предоставляет.",
                fill=WARN, line=ACCENT_2, size=15, bold=True, align="ctr")
        + shape(22, 0.75, 5.0, 3.85, 1.85,
                "Проблема\n\n"
                "Single-node SignalR: события не пересекают границу узла.",
                fill=PANEL, size=13, bold=True)
        + shape(23, 4.75, 5.0, 3.85, 1.85,
                "Решение\n\n"
                "Несколько экземпляров backend за nginx + Redis backplane; "
                "общий код, переключение режима — переменной окружения.",
                fill=PANEL, size=13, bold=True)
        + shape(24, 8.75, 5.0, 3.85, 1.85,
                "Доказательство\n\n"
                "Доставка (без / с) · серия · восстановление подписки · переключение после отказа.",
                fill=PANEL, size=13, bold=True),
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
  <a:themeElements><a:clrScheme name="VKR"><a:dk1><a:srgbClr val="18212B"/></a:dk1><a:lt1><a:srgbClr val="F6F3EC"/></a:lt1><a:dk2><a:srgbClr val="293241"/></a:dk2><a:lt2><a:srgbClr val="FFFFFF"/></a:lt2><a:accent1><a:srgbClr val="0B6E69"/></a:accent1><a:accent2><a:srgbClr val="C76F2E"/></a:accent2><a:accent3><a:srgbClr val="E8F3F1"/></a:accent3><a:accent4><a:srgbClr val="FFF3D8"/></a:accent4><a:accent5><a:srgbClr val="5E6A75"/></a:accent5><a:accent6><a:srgbClr val="D7D2C7"/></a:accent6><a:hlink><a:srgbClr val="0B6E69"/></a:hlink><a:folHlink><a:srgbClr val="0B6E69"/></a:folHlink></a:clrScheme><a:fontScheme name="Aptos"><a:majorFont><a:latin typeface="Aptos"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme><a:fmtScheme name="VKR"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme></a:themeElements>
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
