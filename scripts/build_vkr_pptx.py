from __future__ import annotations

import html
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "pptx"
OUT_PPTX = OUT_DIR / "vkr-defense-draft.pptx"
PRACTICE_OUT_PPTX = OUT_DIR / "practice-defense-draft.pptx"

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


def slide_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
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
            + shape(13, 0.65, 5.2, 11.9, 0.4, "Руководитель: ст. преподаватель С. А. Рогачев",
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
        + shape(13, 0.65, 5.2, 11.9, 0.4, "Руководитель: ст. преподаватель С. А. Рогачев",
                fill="", line="", size=15, align="ctr")
        + shape(14, 0.65, 6.0, 11.9, 0.4, "Санкт-Петербург, 2026",
                fill="", line="", size=14, text_color=MUTED, align="ctr")
    )


def deck_slides(kind: str = "vkr") -> list[str]:
    return [
        # 1. Title
        title_slide(kind),

        # 2. Problem and thesis
        title(10, "Проблема: single-node SignalR теряет события между узлами")
        + shape(20, 0.75, 1.7, 5.7, 2.6,
                "Без межузлового канала\nКаждый экземпляр знает только своих клиентов.\nСобытие, созданное на одном узле, не доходит до клиента на другом.",
                fill=PANEL, size=18)
        + shape(21, 6.75, 1.7, 5.7, 2.6,
                "Цель работы\nВосстановить корректную доставку событий между клиентами, подключенными к разным экземплярам backend-сервиса.",
                fill=SOFT, line=ACCENT, size=18, bold=True),

        # 3. Target architecture
        title(10, "Целевая архитектура")
        + shape(20, 0.7, 1.85, 2.0, 0.7, "Клиент A", fill=PANEL, size=14, bold=True, align="ctr")
        + shape(21, 0.7, 3.55, 2.0, 0.7, "Клиент B", fill=PANEL, size=14, bold=True, align="ctr")
        + shape(22, 3.4, 2.7, 1.7, 0.85, "nginx", fill=SOFT, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(23, 5.8, 1.85, 2.1, 0.7, "app-api-1", fill=PANEL, size=14, bold=True, align="ctr")
        + shape(24, 5.8, 3.55, 2.1, 0.7, "app-api-2", fill=PANEL, size=14, bold=True, align="ctr")
        + shape(25, 8.55, 2.7, 2.5, 0.85, "Redis backplane", fill=SOFT, line=ACCENT, size=14, bold=True, align="ctr")
        + shape(26, 0.7, 5.2, 11.5, 0.55,
                "SignalR-события публикуются между экземплярами через Redis; группы остаются локальным runtime-состоянием.",
                fill="", line="", size=14, text_color=MUTED, align="ctr"),

        # 4. What was built
        title(10, "Что сделано")
        + shape(20, 0.75, 1.7, 5.7, 1.2,
                "1 · Redis backplane для SignalR\nКонфигурируется через REDIS_CONNECTION_STRING",
                fill=PANEL, size=15)
        + shape(21, 0.75, 3.0, 5.7, 1.2,
                "2 · Диагностика узла\nSERVER_INSTANCE_ID, connectionId, machineName",
                fill=PANEL, size=15)
        + shape(22, 6.75, 1.7, 5.7, 1.2,
                "3 · Стенд Docker Compose\napp-api-1, app-api-2, Redis, PostgreSQL, nginx",
                fill=PANEL, size=15)
        + shape(23, 6.75, 3.0, 5.7, 1.2,
                "4 · Node.js-клиент\nDelivery, серия, rejoin, failover",
                fill=PANEL, size=15),

        # 5. Test stand and program
        title(10, "Стенд и программа испытаний")
        + shape(20, 0.75, 1.75, 5.7, 2.5,
                "Два режима\n• С Redis backplane\n• Без Redis backplane\nОдин и тот же код, разница — переменная окружения.",
                fill=SOFT, line=ACCENT, size=15)
        + shape(21, 6.75, 1.75, 5.7, 2.5,
                "Четыре сценария\n• Одиночная доставка\n• Серия из 5 итераций\n• Rejoin после разрыва\n• Failover узла",
                fill=PANEL, size=15),

        # 6. Main result
        title(10, "Главный результат")
        + shape(20, 0.75, 1.7, 5.7, 2.6,
                "Без backplane\ntimeout 10000 мс\nсобытие не доставлено",
                fill=WARN, line=ACCENT_2, size=20, bold=True, align="ctr")
        + shape(21, 6.75, 1.7, 5.7, 2.6,
                "С backplane\nok: true · 5 из 5\np95 = 11,6 мс",
                fill=SOFT, line=ACCENT, size=20, bold=True, align="ctr")
        + shape(22, 0.75, 4.7, 11.7, 0.55,
                "Один код, один сценарий — разница только в наличии межузлового канала.",
                fill="", line="", size=14, text_color=MUTED, align="ctr"),

        # 7. Resilience
        title(10, "Устойчивость: rejoin и failover")
        + shape(20, 0.75, 1.75, 5.7, 2.5,
                "Rejoin после разрыва\nНовый connectionId, повторный JoinReportGroupAsync.\nСобытие после rejoin — 6,6 мс.",
                fill=PANEL, size=15)
        + shape(21, 6.75, 1.75, 5.7, 2.5,
                "Failover узла\nКлиент переподключился через nginx с app-api-2 на app-api-1.\nreconnect + rejoin — 240,3 мс.",
                fill=SOFT, line=ACCENT, size=15),

        # 8. Conclusion
        title(10, "Вывод")
        + shape(20, 0.75, 1.85, 11.7, 1.4,
                "Ограничение single-node WebSocket-архитектуры устранено за счёт распределённого real-time контура.",
                fill=SOFT, line=ACCENT, size=20, bold=True, align="ctr")
        + shape(21, 0.75, 3.55, 3.7, 1.7,
                "Проблема\nБез backplane событие теряется между узлами.",
                fill=PANEL, size=14, bold=True)
        + shape(22, 4.65, 3.55, 3.7, 1.7,
                "Решение\nSignalR + Redis backplane + nginx + два app-api.",
                fill=PANEL, size=14, bold=True)
        + shape(23, 8.55, 3.55, 3.7, 1.7,
                "Доказательство\nDelivery, серия, rejoin, failover.",
                fill=PANEL, size=14, bold=True),
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
        for i, body in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{i}.xml", slide_xml(i, body))
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", slide_rels())
    return out_path


def main(kind: str | None = None):
    selected = kind or ("practice" if "--practice" in sys.argv else "vkr")
    if selected not in {"vkr", "practice"}:
        raise ValueError(f"Unknown deck kind: {selected}")
    print(build(selected))


if __name__ == "__main__":
    main()
