from __future__ import annotations

import html
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "pptx"
OUT_PPTX = OUT_DIR / "vkr-defense-draft.pptx"

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


def title(sid: int, text: str, subtitle: str | None = None) -> str:
    parts = [
        shape(sid, 0.65, 0.45, 11.9, 0.72, text, fill="", line="", size=30, bold=True),
    ]
    if subtitle:
        parts.append(shape(sid + 1, 0.68, 1.08, 10.8, 0.35, subtitle, fill="", line="", size=13, text_color=MUTED))
    return "\n".join(parts)


def footer(n: int) -> str:
    return shape(900, 0.65, 7.12, 12.0, 0.22, f"ВКР · real-time scale-out · {n:02d}", fill="", line="", size=8, text_color=MUTED)


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


def slide_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""


def deck_slides() -> list[str]:
    return [
        title(10, "Горизонтальное масштабирование WebSocket-соединений", "Система отслеживания задач · SignalR · Redis backplane · nginx")
        + shape(20, 0.8, 2.15, 5.7, 2.2, "Тезис\nРазработан и проверен распределенный real-time контур, устраняющий single-node ограничение WebSocket-архитектуры.", fill=SOFT, line=ACCENT, size=22, bold=True)
        + shape(21, 6.85, 2.15, 5.3, 2.2, "Ключевой результат\nСобытие, созданное на app-api-1, доставляется клиенту на app-api-2; после отказа app-api-2 клиент восстанавливается через nginx.", fill=PANEL, line=ACCENT_2, size=21),
        title(10, "Проблема: real-time ломается не в коде события, а в границе узла")
        + shape(20, 0.75, 1.55, 3.55, 3.2, "Single-node\nВсе соединения и группы живут в памяти одного процесса.", fill=PANEL, size=20, bold=True)
        + shape(21, 4.65, 1.55, 3.55, 3.2, "Multi-instance без backplane\nКаждый app-api знает только своих клиентов.", fill=WARN, line=ACCENT_2, size=20, bold=True)
        + shape(22, 8.55, 1.55, 3.55, 3.2, "Следствие\nКлиент на другом узле не получает ReceiveReportPatch.", fill=PANEL, size=20, bold=True),
        title(10, "Целевая архитектура: общий real-time слой поверх нескольких app-api")
        + shape(20, 0.7, 1.55, 2.25, 0.8, "Клиент A", fill=PANEL, size=18, bold=True, align="ctr")
        + shape(21, 0.7, 3.15, 2.25, 0.8, "Клиент B", fill=PANEL, size=18, bold=True, align="ctr")
        + shape(22, 3.45, 2.35, 1.8, 0.9, "nginx", fill=SOFT, line=ACCENT, size=18, bold=True, align="ctr")
        + shape(23, 5.85, 1.55, 2.15, 0.8, "app-api-1", fill=PANEL, size=18, bold=True, align="ctr")
        + shape(24, 5.85, 3.15, 2.15, 0.8, "app-api-2", fill=PANEL, size=18, bold=True, align="ctr")
        + shape(25, 8.65, 2.35, 2.4, 0.9, "Redis backplane", fill=SOFT, line=ACCENT, size=17, bold=True, align="ctr")
        + shape(26, 3.0, 5.05, 7.4, 0.65, "События SignalR публикуются между экземплярами, а группы остаются локальным runtime-состоянием.", fill="", line="", size=17, text_color=MUTED, align="ctr"),
        title(10, "Что реализовано в отдельной ветке thesis/realtime-scaleout")
        + shape(20, 0.75, 1.45, 5.6, 1.0, "1 · Redis backplane для SignalR\nКонфигурируется через REDIS_CONNECTION_STRING", fill=PANEL, size=18)
        + shape(21, 0.75, 2.65, 5.6, 1.0, "2 · Диагностика узла\nSERVER_INSTANCE_ID, connectionId, machineName", fill=PANEL, size=18)
        + shape(22, 6.75, 1.45, 5.6, 1.0, "3 · Multi-instance Docker Compose\napp-api-1, app-api-2, Redis, PostgreSQL, nginx", fill=PANEL, size=18)
        + shape(23, 6.75, 2.65, 5.6, 1.0, "4 · Автоматизированный клиент\nDelivery, serial, rejoin и failover сценарии", fill=PANEL, size=18)
        + shape(24, 1.2, 4.45, 10.8, 0.95, "Важная граница: проверяется серверный real-time контур, а не полнота пользовательского интерфейса.", fill=WARN, line=ACCENT_2, size=19, bold=True, align="ctr"),
        title(10, "Стенд испытаний: минимальный, но проверяемый")
        + shape(20, 0.8, 1.45, 3.5, 3.8, "Состав\npostgres_app_thesis\nredis_app_thesis\napp-api-1\napp-api-2\nnginx_app_thesis", fill=PANEL, size=19)
        + shape(21, 4.75, 1.45, 3.5, 3.8, "Две конфигурации\nС Redis backplane\nБез Redis backplane\n\nОдин и тот же код, разная настройка REDIS_CONNECTION_STRING", fill=SOFT, line=ACCENT, size=18)
        + shape(22, 8.7, 1.45, 3.5, 3.8, "Команды\nnode scripts/realtime-scaleout-check.mjs\nTHESIS_ITERATIONS=5\nTHESIS_SCENARIO=failover", fill=PANEL, size=17),
        title(10, "Главная проверка: без backplane проблема воспроизводится")
        + shape(20, 0.9, 1.55, 5.45, 2.7, "Без Redis backplane\nReceiveReportPatch timed out after 10000ms", fill=WARN, line=ACCENT_2, size=25, bold=True, align="ctr")
        + shape(21, 6.85, 1.55, 5.45, 2.7, "С Redis backplane\nok: true\napp-api-1 → app-api-2", fill=SOFT, line=ACCENT, size=25, bold=True, align="ctr")
        + shape(22, 1.2, 4.75, 10.6, 0.75, "Итог: проблема не декларативная — она воспроизводится на том же стенде и устраняется только при включенной межузловой доставке.", fill="", line="", size=19, text_color=MUTED, align="ctr"),
        title(10, "Серийный прогон показывает повторяемость, а не разовый успех")
        + shape(20, 0.85, 1.55, 2.35, 2.2, "5 / 5\nуспешно", fill=SOFT, line=ACCENT, size=30, bold=True, align="ctr")
        + shape(21, 3.55, 1.55, 2.35, 2.2, "8,4 мс\navg", fill=PANEL, size=30, bold=True, align="ctr")
        + shape(22, 6.25, 1.55, 2.35, 2.2, "9,1 мс\np50", fill=PANEL, size=30, bold=True, align="ctr")
        + shape(23, 8.95, 1.55, 2.35, 2.2, "11,6 мс\np95", fill=PANEL, size=30, bold=True, align="ctr")
        + shape(24, 1.2, 4.45, 10.5, 0.9, "Локальный короткий прогон не является нагрузочным тестом, но доказывает повторяемость ключевого свойства.", fill=WARN, line=ACCENT_2, size=19, align="ctr"),
        title(10, "Устойчивость: подписка восстанавливается после разрыва и отказа узла")
        + shape(20, 0.85, 1.55, 5.4, 2.5, "Rejoin после разрыва\nНовый connectionId\nПовторный JoinReportGroupAsync\nСобытие после rejoin: 6,6 мс", fill=PANEL, size=20, bold=True)
        + shape(21, 6.55, 1.55, 5.4, 2.5, "Failover app-api-2\nКлиент через nginx перешел app-api-2 → app-api-1\nreconnect + rejoin: 240,3 мс\nследующее событие получено", fill=SOFT, line=ACCENT, size=19, bold=True)
        + shape(22, 1.1, 4.75, 10.8, 0.65, "Для WebSocket-only проверки через nginx используется skipNegotiation, чтобы не зависеть от sticky sessions на этапе negotiate.", fill="", line="", size=17, text_color=MUTED, align="ctr"),
        title(10, "Что это дает системе отслеживания задач")
        + shape(20, 0.8, 1.45, 3.55, 3.25, "Масштабирование\nМожно запускать несколько backend-экземпляров без фрагментации real-time пространства.", fill=PANEL, size=19, bold=True)
        + shape(21, 4.75, 1.45, 3.55, 3.25, "Наблюдаемость\nserverInstanceId и connectionId превращают демонстрацию в проверяемый эксперимент.", fill=PANEL, size=19, bold=True)
        + shape(22, 8.7, 1.45, 3.55, 3.25, "Воспроизводимость\nCompose-стенд, override без backplane и Node.js-клиент фиксируют результат.", fill=PANEL, size=19, bold=True)
        + shape(23, 1.1, 5.25, 11.0, 0.5, "Следующий промышленный шаг: длинная серия, больше клиентов, p99, поведение при недоступности Redis.", fill="", line="", size=17, text_color=MUTED, align="ctr"),
        title(10, "Вывод для защиты")
        + shape(20, 0.9, 1.35, 11.3, 1.35, "Разработан распределенный real-time контур для системы отслеживания задач, устраняющий single-node ограничение SignalR/WebSocket-архитектуры.", fill=SOFT, line=ACCENT, size=25, bold=True, align="ctr")
        + shape(21, 0.9, 3.05, 3.45, 1.55, "Проблема\nБез backplane событие не доходит между узлами.", fill=PANEL, size=19, bold=True)
        + shape(22, 4.85, 3.05, 3.45, 1.55, "Решение\nSignalR + Redis backplane + nginx + два app-api.", fill=PANEL, size=19, bold=True)
        + shape(23, 8.8, 3.05, 3.45, 1.55, "Доказательство\nDelivery, series, rejoin, failover.", fill=PANEL, size=19, bold=True)
        + shape(24, 1.2, 5.25, 10.5, 0.55, "Документ удержан в компактном формате до 35 страниц и подходит как база отчета по практике.", fill="", line="", size=18, text_color=MUTED, align="ctr"),
    ]


def content_types(slide_count: int) -> str:
    overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
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


def build() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slides = deck_slides()
    with zipfile.ZipFile(OUT_PPTX, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types(len(slides)))
        z.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        z.writestr("ppt/_rels/presentation.xml.rels", presentation_rels(len(slides)))
        for path, content in static_parts().items():
            z.writestr(path, content)
        for i, body in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{i}.xml", slide_xml(i, body))
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels())
    return OUT_PPTX


if __name__ == "__main__":
    print(build())
