"""Exportacion del documento a Word (.docx) con estructura y referencias APA."""
from __future__ import annotations

import io

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


def build_docx(
    title: str,
    author: str,
    sections: list[tuple[str, str]],
    references: list[str],
) -> bytes:
    """Construye el .docx en memoria y devuelve los bytes para descargar.

    sections: lista de (titulo_seccion, contenido)
    references: lista de referencias ya formateadas en APA
    """
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)

    # Portada simple
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = t.add_run(title or "Tesis")
    run.bold = True
    run.font.size = Pt(18)

    if author:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(author)

    doc.add_page_break()

    # Secciones
    for heading, content in sections:
        doc.add_heading(heading, level=1)
        for para in (content or "").split("\n"):
            para = para.strip()
            if para:
                body = doc.add_paragraph(para)
                body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Referencias
    if references:
        doc.add_page_break()
        doc.add_heading("Referencias", level=1)
        for ref in references:
            p = doc.add_paragraph(ref)
            p.paragraph_format.left_indent = Pt(36)
            p.paragraph_format.first_line_indent = Pt(-36)  # sangria francesa

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
