from thesisai.search import search_articles
from thesisai.writing import chapters_for, draft_chapter
from thesisai.citations import build_bibliography
from thesisai.export import build_docx

TEMA = ("Calidad del servicio educativo y satisfaccion de los estudiantes "
        "en CETPROs de Andahuaylas, 2026")
arts = search_articles("calidad servicio educativo satisfaccion estudiantes institutos", 2018, 2026, limit=6)
caps = {c[0]: c for c in chapters_for("proyecto")}
gen = []
for name in ["CAPÍTULO I. EL PROBLEMA", "CAPÍTULO III. METODOLOGÍA", "Matriz de consistencia"]:
    t, k, g = caps[name]
    print("Redactando:", name)
    txt, used = draft_chapter(TEMA, t, k, g, arts)
    gen.append((name, txt))
    print(f"  OK {used} ({len(txt)} chars)")

data = build_docx(TEMA, "Bray Yusman (ejemplo)", gen, build_bibliography(arts))
with open("ejemplo_tesis_unajma_v4.docx", "wb") as f:
    f.write(data)
print(f"Listo: ejemplo_tesis_unajma_v4.docx ({len(data)} bytes)")
