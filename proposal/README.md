# proposal

Proposal lomba dalam LaTeX, mengikuti format template resmi (`template-proposal-hackathon-chip-2026.pdf`).

| File | Isi |
|---|---|
| `main.tex` | Sumber proposal (5 bagian wajib + tim, luaran, rencana bootcamp) |
| `main.pdf` | Hasil kompilasi |
| `figures/` | Gambar yang dipakai di proposal |

## Kompilasi

```bash
cd proposal
pdflatex main.tex
pdflatex main.tex   # dua kali agar nomor gambar & referensi benar
```

Atau unggah folder ini ke Overleaf (compiler: pdfLaTeX).

Teks berwarna **merah dalam kurung siku** di PDF adalah bagian yang masih harus diisi tim.
