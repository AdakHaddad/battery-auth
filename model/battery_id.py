"""Model referensi Secure Battery Identity Chip.

Model ini meniru perilaku chip, stasiun, dan basis data identitas pada
tingkat protokol. Kunci PUF diganti kunci tetap per chip, sesuai rencana
jalur kritis (kunci tetap dulu, PUF kemudian). Respons yang dihitung model
menjadi acuan kebenaran untuk testbench RTL.
"""

import hashlib
import hmac
import os
from dataclasses import dataclass, field

NONCE_BYTES = 32      # nonce 256 bit
HELPER_BYTES = 64     # helper data 512 bit
ID_BYTES = 8          # ID 64 bit


def derive_id(helper_data: bytes) -> bytes:
    """ID = 64 bit pertama SHA-256(helper data)."""
    return hashlib.sha256(helper_data).digest()[:ID_BYTES]


def derive_key(stable_bits: bytes, helper_data: bytes) -> bytes:
    """K = SHA-256(bit stabil || helper data)."""
    return hashlib.sha256(stable_bits + helper_data).digest()


def response(key: bytes, nonce: bytes, chip_id: bytes) -> bytes:
    """Respons = HMAC-SHA-256(K, nonce || ID)."""
    return hmac.new(key, nonce + chip_id, hashlib.sha256).digest()


@dataclass
class Chip:
    """Chip di dalam pack baterai. Kunci hanya dibentuk saat dibutuhkan."""

    stable_bits: bytes                      # pengganti keluaran fuzzy extractor
    locked: bool = False

    def auth(self, nonce: bytes, helper_data: bytes) -> bytes | None:
        if self.locked:
            return None
        chip_id = derive_id(helper_data)
        key = derive_key(self.stable_bits, helper_data)
        resp = response(key, nonce, chip_id)
        del key                             # kunci dihapus setelah dipakai
        return resp

    def tamper(self) -> None:
        """Gangguan clock atau casing terbuka: kunci dihapus, chip terkunci."""
        self.locked = True


@dataclass
class Database:
    """Basis data identitas milik pihak tepercaya (kunci disimpan di HSM)."""

    hsm: dict = field(default_factory=dict)        # ID -> kunci
    records: dict = field(default_factory=dict)    # ID -> helper data, riwayat
    pending: dict = field(default_factory=dict)    # nonce -> ID
    blocked: set = field(default_factory=set)

    def enroll(self, chip: Chip, helper_data: bytes, capacity_ah: float) -> bytes:
        chip_id = derive_id(helper_data)
        self.hsm[chip_id] = derive_key(chip.stable_bits, helper_data)
        self.records[chip_id] = {"helper": helper_data, "history": [capacity_ah]}
        return chip_id

    def issue_nonce(self, chip_id: bytes) -> bytes:
        nonce = os.urandom(NONCE_BYTES)
        self.pending[nonce] = chip_id
        return nonce

    def verify(self, chip_id: bytes, nonce: bytes, resp: bytes | None,
               capacity_ah: float, chip_locked: bool = False) -> bool:
        if chip_locked:
            self.blocked.add(chip_id)
        if chip_id in self.blocked or chip_id not in self.hsm:
            return False
        if self.pending.pop(nonce, None) != chip_id:    # nonce sekali pakai
            return False
        if resp is None:
            return False
        expected = response(self.hsm[chip_id], nonce, chip_id)
        if not hmac.compare_digest(expected, resp):
            return False
        history = self.records[chip_id]["history"]
        if capacity_ah > history[-1] * 1.05:            # kapasitas naik tidak wajar
            return False
        history.append(capacity_ah)
        return True


def swap(db: Database, chip: Chip, helper_data: bytes, capacity_ah: float) -> bool:
    """Satu penukaran baterai di stasiun: nonce -> chip -> basis data."""
    chip_id = derive_id(helper_data)
    nonce = db.issue_nonce(chip_id)
    resp = chip.auth(nonce, helper_data)
    return db.verify(chip_id, nonce, resp, capacity_ah, chip.locked)
