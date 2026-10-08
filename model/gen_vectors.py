"""Membuat vektor uji emas untuk RTL SHA-256 dan HMAC.

Jalankan dari folder model/:  python gen_vectors.py
Keluaran ditulis ke sim/vectors/. Semua nilai dalam hex big-endian, satu
vektor per baris, sehingga mudah dibaca $readmemh atau skrip Python di HPS.

File yang dihasilkan:
  sha256_blocks.hex  : H_awal(256) | blok(512) | H_akhir(256)
                       untuk menguji inti kompresi satu blok demi satu blok.
  sha256_msgs.txt    : pesan (hex) dan digest, untuk uji SHA-256 utuh.
  hmac_auth.hex      : K(256) | nonce(256) | ID(64) | respons(256)
                       sesuai respons chip = HMAC-SHA-256(K, nonce || ID).
  hmac_debug.txt     : nilai antara HMAC (hash dalam) untuk melacak kesalahan.
"""

import hashlib
import hmac
import os
import random
import struct
from pathlib import Path

from battery_id import response

OUT = Path(__file__).resolve().parent.parent / "sim" / "vectors"

H0 = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]


def _rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xffffffff


def compress(state, block):
    """Satu kompresi SHA-256 (64 ronde), sama dengan yang dikerjakan inti RTL."""
    w = list(struct.unpack(">16I", block))
    for t in range(16, 64):
        s0 = _rotr(w[t - 15], 7) ^ _rotr(w[t - 15], 18) ^ (w[t - 15] >> 3)
        s1 = _rotr(w[t - 2], 17) ^ _rotr(w[t - 2], 19) ^ (w[t - 2] >> 10)
        w.append((w[t - 16] + s0 + w[t - 7] + s1) & 0xffffffff)
    a, b, c, d, e, f, g, h = state
    for t in range(64):
        t1 = (h + (_rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)) + ((e & f) ^ (~e & g)) + K[t] + w[t]) & 0xffffffff
        t2 = ((_rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & 0xffffffff
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & 0xffffffff, c, b, a, (t1 + t2) & 0xffffffff
    return [(x + y) & 0xffffffff for x, y in zip(state, [a, b, c, d, e, f, g, h])]


def pad(msg):
    ml = len(msg) * 8
    msg += b"\x80" + b"\x00" * ((55 - len(msg)) % 64) + struct.pack(">Q", ml)
    return [msg[i:i + 64] for i in range(0, len(msg), 64)]


def words_hex(words):
    return "".join(f"{x:08x}" for x in words)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(2026)          # deterministik agar vektor bisa direproduksi

    messages = [
        b"",
        b"abc",
        b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
        bytes(rng.getrandbits(8) for _ in range(40)),     # ukuran nonce || ID
        bytes(rng.getrandbits(8) for _ in range(100)),
    ]

    block_lines, msg_lines = [], []
    for msg in messages:
        state = H0[:]
        for blk in pad(msg):
            new = compress(state, blk)
            block_lines.append(words_hex(state) + blk.hex() + words_hex(new))
            state = new
        assert words_hex(state) == hashlib.sha256(msg).hexdigest()
        msg_lines.append(f"{msg.hex() or '-'} {hashlib.sha256(msg).hexdigest()}")

    auth_lines, debug_lines = [], []
    for _ in range(16):
        key = bytes(rng.getrandbits(8) for _ in range(32))
        nonce = bytes(rng.getrandbits(8) for _ in range(32))
        chip_id = bytes(rng.getrandbits(8) for _ in range(8))
        resp = response(key, nonce, chip_id)
        assert resp == hmac.new(key, nonce + chip_id, hashlib.sha256).digest()
        inner = hashlib.sha256(bytes(b ^ 0x36 for b in key.ljust(64, b"\x00")) + nonce + chip_id).digest()
        auth_lines.append(key.hex() + nonce.hex() + chip_id.hex() + resp.hex())
        debug_lines.append(f"K={key.hex()} nonce={nonce.hex()} ID={chip_id.hex()} "
                           f"inner={inner.hex()} resp={resp.hex()}")

    (OUT / "sha256_blocks.hex").write_text("\n".join(block_lines) + "\n")
    (OUT / "sha256_msgs.txt").write_text("\n".join(msg_lines) + "\n")
    (OUT / "hmac_auth.hex").write_text("\n".join(auth_lines) + "\n")
    (OUT / "hmac_debug.txt").write_text("\n".join(debug_lines) + "\n")
    print(f"{len(block_lines)} blok SHA-256, {len(msg_lines)} pesan, {len(auth_lines)} vektor HMAC -> {OUT}")


if __name__ == "__main__":
    main()
