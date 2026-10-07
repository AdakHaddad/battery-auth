"""Urutkan \\bibitem di main.tex sesuai urutan sitasi pertama di teks.

Jalankan ulang setiap kali sitasi ditambah atau dipindah:
    python urutkan_referensi.py
lalu kompilasi ulang main.tex. Referensi yang tidak dikutip dilaporkan
dan ditaruh di akhir daftar.
"""
import re
import sys
from pathlib import Path

TEX = Path(__file__).with_name("main.tex")

src = TEX.read_text(encoding="utf-8")
bib_start = src.index("\\begin{thebibliography}")
bib_end = src.index("\\end{thebibliography}")

# Urutan sitasi pertama (abaikan baris komentar)
body = "\n".join(l for l in src[:bib_start].splitlines() if not l.lstrip().startswith("%"))
order = []
for group in re.findall(r"\\cite\{([^}]*)\}", body):
    for key in (k.strip() for k in group.split(",")):
        if key not in order:
            order.append(key)

# Pisahkan blok bibliografi menjadi kepala + item
bib = src[bib_start:bib_end]
head_end = bib.index("\\bibitem")
head, items_text = bib[:head_end], bib[head_end:]
items = {}
for chunk in re.split(r"(?=\\bibitem\{)", items_text):
    m = re.match(r"\\bibitem\{([^}]*)\}", chunk)
    if m:
        items[m.group(1)] = chunk.rstrip() + "\n"

missing = [k for k in order if k not in items]
if missing:
    sys.exit(f"Dikutip tetapi tidak ada di daftar pustaka: {missing}")

uncited = [k for k in items if k not in order]
new_bib = head + "".join(items[k] for k in order + uncited)
TEX.write_text(src[:bib_start] + new_bib + src[bib_end:], encoding="utf-8")

print("Urutan:", ", ".join(f"[{i}] {k}" for i, k in enumerate(order + uncited, 1)))
if uncited:
    print("Peringatan, tidak dikutip di teks:", ", ".join(uncited))
