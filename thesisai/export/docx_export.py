"""Exportacion a Word (.docx) con el formato oficial UNAJMA (Anexo 08)."""
from __future__ import annotations

import io

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt


def _add_page_number(paragraph) -> None:
    """Inserta un campo de numero de pagina (arabigo) en el parrafo dado."""
    run = paragraph.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


def _apply_unajma_format(doc: Document) -> None:
    """Aplica el formato del Anexo 08 de la Escuela de Posgrado UNAJMA."""
    # Margenes: izquierdo y superior 4 cm; derecho e inferior 2.5 cm.
    for section in doc.sections:
        section.left_margin = Cm(4)
        section.top_margin = Cm(4)
        section.right_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        # Numero de pagina abajo a la derecha.
        footer = section.footer
        fp = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        _add_page_number(fp)

    # Estilo Normal: Times New Roman 12, justificado, interlineado 1.5,
    # espaciado antes 12 / despues 6.
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    pf = normal.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_before = Pt(12)
    pf.space_after = Pt(6)


def build_docx(
    title: str,
    author: str,
    sections: list[tuple[str, str]],
    references: list[str],
) -> bytes:
    """Construye el .docx (formato UNAJMA) y devuelve los bytes para descargar.

    sections: lista de (titulo_seccion, contenido)
    references: lista de referencias ya formateadas en APA
    """
    doc = Document()
    _apply_unajma_format(doc)

    # ---- Portada (sin marco, centrada) ----
    for _ in range(3):
        doc.add_paragraph()
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = t.add_run((title or "Tesis").upper())
    run.bold = True
    run.font.size = Pt(16)
    run.font.name = "Times New Roman"

    if author:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(author)

    doc.add_page_break()

    # ---- Secciones ----
    for heading, content in sections:
        h = doc.add_heading(heading, level=1)
        for r in h.runs:
            r.font.name = "Times New Roman"
        for para in (content or "").split("\n"):
            para = para.strip()
            if para:
                body = doc.add_paragraph(para)
                body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # ---- Referencias (sangria francesa) ----
    if references:
        doc.add_page_break()
        doc.add_heading("Referencias bibliográficas", level=1)
        for ref in references:
            p = doc.add_paragraph(ref)
            p.paragraph_format.left_indent = Cm(1.25)
            p.paragraph_format.first_line_indent = Cm(-1.25)  # sangria francesa

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
