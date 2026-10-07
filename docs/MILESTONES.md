# Milestone Proyek

Rencana kerja dari pendaftaran sampai final. Centang `[x]` setiap tugas yang selesai dan isi kolom PIC (penanggung jawab).

**Peran yang dipakai di bawah:**
- **RTL**: perancang Verilog
- **VER**: verifikasi (cocotb, model Python)
- **SEC**: analis keamanan (threat model, uji serangan)
- **SYS**: sistem, bisnis, dan dokumen

| # | Milestone | Tenggat | Hasil akhir |
|---|---|---|---|
| M0 | Persiapan & registrasi | 7 Okt (malam) | Tim terdaftar, repo aktif, tools terpasang |
| M1 | Proposal terkirim | 8 Okt (≥3 jam sebelum deadline) | PDF proposal 5 bagian |
| M2 | Fondasi teknis | 12 Okt | SHA-256 + HMAC lolos simulasi, prototipe PUF di FPGA |
| M3 | Pengumuman Top 5 | 13 Okt | Keputusan lanjut |
| M4 | Integrasi pra-bootcamp | 17 Okt | Chip lengkap jalan di DE10-Nano, demo dasar |
| M5 | Bootcamp | 18–20 Okt | Demo serangan, metrik, laporan teknis |
| M6 | Final & presentasi | 21–22 Okt | Pitch, demo live, video cadangan |

---

## M0 — Persiapan & registrasi (7 Okt malam)

| Tugas | PIC | Selesai |
|---|---|---|
| Isi formulir registrasi di summit.peruri.co.id/hackathon | SYS | [ ] |
| Buat repo **Private** di GitHub, push, undang semua anggota | SYS | [ ] |
| Tanyakan ke panitia: jam deadline pasti, format file, perlu tanda tangan dosen atau tidak, board yang disediakan, dan boleh tidaknya kode disiapkan sebelum bootcamp | SYS | [ ] |
| Pasang tools: Verilator, cocotb, Icarus, Yosys, Python 3, Quartus Prime Lite | RTL, VER | [ ] |
| Clone desain TT07: SHA-256 dan RO-PUF (lihat `docs/referensi/teknis/`) | RTL | [ ] |

## M1 — Proposal terkirim (8 Okt)

Struktur wajib sesuai buku panduan, berurutan:

| Tugas | PIC | Selesai |
|---|---|---|
| **1. Ringkasan Ide:** masalah, solusi, chip, pengguna, dampak, dalam bahasa awam | SYS | [ ] |
| **2. Latar Belakang:** ekosistem tukar baterai, bahaya baterai palsu, regulasi (Perpres 55/2019, 79/2023, RUPTL, IBC), dan alasan PERURI menjadi pihak tepercaya | SYS | [ ] |
| Tabel threat model: penyerang → aset → serangan → blok chip yang menangkal | SEC | [ ] |
| Pembeda dari produk yang sudah ada (Infineon OPTIGA, chip autentikasi TI) | SEC, SYS | [ ] |
| **3. Proposed Chip Design:** diagram blok, I/O, protokol challenge-response, antarmuka ke BMS, rencana daya | RTL | [ ] |
| Strategi verifikasi: model Python, cocotb, uji NIST SP800-22, metrik PUF | VER | [ ] |
| Estimasi resource dari sintesis Yosys baseline SHA-256 (angka nyata, bukan TBD) | RTL | [ ] |
| Target: FPGA Cyclone V (DE10-Nano), opsional ASIC SKY130 | RTL | [ ] |
| **4. Referensi:** datasheet TT07, datasheet Peruri chip, FIPS 180-4, FIPS 198-1 (HMAC), NIST SP800-22, regulasi energi | SYS | [ ] |
| **5. Lampiran:** rencana bootcamp 3 hari, identitas tim, pembagian peran | SYS | [ ] |
| Review oleh dosen pembimbing | Semua | [ ] |
| Ekspor PDF ke `proposal/proposal-final.pdf`, lalu kirim | SYS | [ ] |

## M2 — Fondasi teknis (9–12 Okt)

Jangan menunggu pengumuman Top 5. Bootcamp hanya 3 hari, jadi bagian dasar harus sudah jalan sebelumnya.

| Tugas | PIC | Selesai |
|---|---|---|
| Model Python: HMAC-SHA-256 dan protokol challenge-response (`model/`) | VER | [ ] |
| SHA-256 TT07 lolos simulasi cocotb terhadap vektor uji FIPS | RTL, VER | [ ] |
| Wrapper HMAC di atas SHA-256, cocok dengan model Python | RTL | [ ] |
| Prototipe RO-PUF di DE10-Nano: baca respons mentah, ukur stabilitas | RTL, SEC | [ ] |
| Sintesis Quartus pertama: catat resource dan Fmax | RTL | [ ] |

## M3 — Pengumuman Top 5 (13 Okt)

- [ ] Kalau lolos, lanjut ke M4.
- [ ] Kalau tidak lolos, rapikan repo sebagai portofolio dan tulis catatan pembelajaran.

## M4 — Integrasi pra-bootcamp (13–17 Okt)

| Tugas | PIC | Selesai |
|---|---|---|
| Fuzzy extractor PUF (majority voting + repetition code) agar kunci bit-exact | RTL | [ ] |
| Kontroler challenge-response (FSM): terima nonce, hitung HMAC, kirim respons | RTL | [ ] |
| Penandatanganan log: chip menandatangani data dari BMS, tanpa menyimpan | RTL | [ ] |
| Detektor glitch clock/tegangan dan logika zeroize/lock | RTL, SEC | [ ] |
| Antarmuka UART/SPI ke PC yang berperan sebagai "stasiun SPBKLU" + skrip verifier Python | VER | [ ] |
| Simulasi top-level lengkap dengan cocotb | VER | [ ] |
| Build di DE10-Nano: demo baterai asli diterima | RTL | [ ] |
| **Rencana cadangan:** mode kunci tetap kalau PUF belum stabil (diakui terbuka) | RTL | [ ] |
| Draf slide presentasi | SYS | [ ] |

## M5 — Bootcamp (18–20 Okt)

| Hari | Fokus | Hasil |
|---|---|---|
| 1 | Perbaikan dari masukan mentor, stabilkan integrasi | Demo dasar stabil di board |
| 2 | Metrik dan serangan | Uniqueness & reliability PUF (Hamming distance), latensi autentikasi, resource, Fmax; demo kloning ditolak, log palsu ditolak, glitch memicu zeroize |
| 3 | Finalisasi | Laporan teknis singkat, rekaman video demo, repo rapi |

- [ ] Hari 1 selesai
- [ ] Hari 2 selesai
- [ ] Hari 3 selesai

## M6 — Final & presentasi (21–22 Okt)

| Tugas | PIC | Selesai |
|---|---|---|
| Pitch deck final: masalah → solusi → demo → metrik → peran PERURI → rencana lanjut | SYS | [ ] |
| Daftar jawaban tanya-jawab: beda dengan OPTIGA, kenapa PERURI, manajemen kunci, tanpa NVM, side-channel, biaya per chip | SEC, SYS | [ ] |
| Gladi presentasi minimal 2 kali, dengan waktu dihitung | Semua | [ ] |
| Video demo cadangan, untuk berjaga kalau board bermasalah saat live | VER | [ ] |
| Board, kabel, dan laptop dicek H-1 | RTL | [ ] |
