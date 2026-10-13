"""Read a .docx into an ordered list of paragraph blocks using only the Python standard library.

Each block: {"text": str, "links": [{"text","url"}], "images": ["word/media/imageN.png"]}
"""
import re
import zipfile
import xml.etree.ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
V = "urn:schemas-microsoft-com:vml"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"


def _rels(z):
    root = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    out = {}
    for rel in root.findall(f"{{{PR}}}Relationship"):
        out[rel.get("Id")] = rel.get("Target")
    return out


def _run_text(el):
    parts = []
    for node in el.iter():
        tag = node.tag.split("}")[-1]
        if tag == "t" and node.text:
            parts.append(node.text)
        elif tag == "tab":
            parts.append("\t")
        elif tag in ("br", "cr"):
            parts.append("\n")
    return "".join(parts)


def _is_bold(run):
    rpr = run.find(f"{{{W}}}rPr")
    if rpr is None:
        return False
    b = rpr.find(f"{{{W}}}b")
    return b is not None and b.get(f"{{{W}}}val", "true") not in ("0", "false")


def _md(p):
    """Paragraph text with **bold** markers (bold runs from Word)."""
    segs = []
    for r in p.iter(f"{{{W}}}r"):
        t = _run_text(r)
        if t:
            segs.append([t, _is_bold(r)])
    merged = []
    for t, b in segs:
        if merged and merged[-1][1] == b:
            merged[-1][0] += t
        else:
            merged.append([t, b])
    out = ""
    for t, b in merged:
        if b and t.strip():
            lead = t[:len(t) - len(t.lstrip())]
            trail = t[len(t.rstrip()):]
            out += f"{lead}**{t.strip()}**{trail}"
        else:
            out += t
    return out.replace("\u00a0", " ")


def read_blocks(path):
    with zipfile.ZipFile(path) as z:
        rels = _rels(z)
        root = ET.fromstring(z.read("word/document.xml"))
        body = root.find(f"{{{W}}}body")
        blocks = []
        # Paragraphs inside tables are walked in document order too
        for p in body.iter(f"{{{W}}}p"):
            text_parts, links, images = [], [], []
            for child in p:
                tag = child.tag.split("}")[-1]
                if tag == "hyperlink":
                    t = _run_text(child)
                    rid = child.get(f"{{{R}}}id")
                    if rid and rid in rels:
                        links.append({"text": t.strip(), "url": rels[rid].strip()})
                    text_parts.append(t)
                elif tag in ("r", "ins", "smartTag", "sdt"):
                    text_parts.append(_run_text(child))
                for blip in child.iter(f"{{{A}}}blip"):
                    rid = blip.get(f"{{{R}}}embed")
                    if rid in rels:
                        images.append("word/" + rels[rid])
                for img in child.iter(f"{{{V}}}imagedata"):
                    rid = img.get(f"{{{R}}}id")
                    if rid in rels:
                        images.append("word/" + rels[rid])
            # Field-code hyperlinks: HYPERLINK "url"
            instr = "".join(n.text or "" for n in p.iter(f"{{{W}}}instrText"))
            for m in re.finditer(r'HYPERLINK\s+"([^"]+)"', instr):
                links.append({"text": "", "url": m.group(1)})
            text = "".join(text_parts).replace(" ", " ")
            if text.strip() or images:
                blocks.append({"text": text, "md": _md(p), "links": links, "images": images})
        return blocks


def read_media(path, member):
    with zipfile.ZipFile(path) as z:
        return z.read(member)


if __name__ == "__main__":
    import json, sys
    for i, b in enumerate(read_blocks(sys.argv[1])):
        print(i, json.dumps(b, ensure_ascii=False)[:220])


def read_tables(path):
    """Return every table in the doc as a list of rows; each row is a list of cell texts."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    tables = []
    for tbl in root.iter(f"{{{W}}}tbl"):
        rows = []
        for tr in tbl.findall(f"{{{W}}}tr"):
            cells = []
            for tc in tr.findall(f"{{{W}}}tc"):
                paras = []
                for p in tc.iter(f"{{{W}}}p"):
                    paras.append(_run_text(p))
                cells.append(" ".join(t.strip() for t in paras if t.strip()))
            rows.append(cells)
        tables.append(rows)
    return tables
