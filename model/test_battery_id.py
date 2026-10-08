"""Uji model referensi. Jalankan dengan: python -m unittest -v model/test_battery_id.py"""

import hashlib
import hmac
import os
import unittest

from battery_id import Chip, Database, HELPER_BYTES, response, swap


class TestSha256Fips180(unittest.TestCase):
    """Vektor uji FIPS 180-4 yang juga akan dipakai untuk RTL SHA-256."""

    VECTORS = [
        (b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
        (b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
         "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
    ]

    def test_vectors(self):
        for msg, digest in self.VECTORS:
            with self.subTest(msg=msg[:8]):
                self.assertEqual(hashlib.sha256(msg).hexdigest(), digest)


class TestHmacRfc4231(unittest.TestCase):
    """Vektor uji RFC 4231 untuk HMAC-SHA-256 (kasus 1-4, 6, 7)."""

    VECTORS = [
        (b"\x0b" * 20, b"Hi There",
         "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"),
        (b"Jefe", b"what do ya want for nothing?",
         "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"),
        (b"\xaa" * 20, b"\xdd" * 50,
         "773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe"),
        (bytes(range(1, 26)), b"\xcd" * 50,
         "82558a389a443c0ea4cc819899f2083a85f0faa3e578f8077a2e3ff46729665b"),
        (b"\xaa" * 131, b"Test Using Larger Than Block-Size Key - Hash Key First",
         "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54"),
        (b"\xaa" * 131,
         b"This is a test using a larger than block-size key and a larger than "
         b"block-size data. The key needs to be hashed before being used by the "
         b"HMAC algorithm.",
         "9b09ffa71b942fcb27635fbcd5b0e944bfdc63644f0713938a7f51535c3a35e2"),
    ]

    def test_vectors(self):
        for i, (key, msg, mac) in enumerate(self.VECTORS):
            with self.subTest(case=i):
                self.assertEqual(hmac.new(key, msg, hashlib.sha256).hexdigest(), mac)


class TestProtocol(unittest.TestCase):
    """Skenario demo pada tingkat protokol (R2, R3, R4)."""

    def setUp(self):
        self.db = Database()
        self.helper = os.urandom(HELPER_BYTES)
        self.chip = Chip(stable_bits=os.urandom(32))
        self.chip_id = self.db.enroll(self.chip, self.helper, capacity_ah=30.0)

    def test_genuine_accepted(self):
        self.assertTrue(swap(self.db, self.chip, self.helper, 29.5))

    def test_clone_rejected(self):
        clone = Chip(stable_bits=os.urandom(32))     # sidik jari silikon berbeda
        self.assertFalse(swap(self.db, clone, self.helper, 29.5))

    def test_replay_rejected(self):
        nonce = self.db.issue_nonce(self.chip_id)
        resp = self.chip.auth(nonce, self.helper)
        self.assertTrue(self.db.verify(self.chip_id, nonce, resp, 29.5))
        self.assertFalse(self.db.verify(self.chip_id, nonce, resp, 29.5))

    def test_tampered_helper_data_rejected(self):
        bad = bytearray(self.helper)
        bad[0] ^= 1
        nonce = self.db.issue_nonce(self.chip_id)
        resp = self.chip.auth(nonce, bytes(bad))
        self.assertFalse(self.db.verify(self.chip_id, nonce, resp, 29.5))

    def test_tamper_locks_and_blocks_id(self):
        self.chip.tamper()
        self.assertFalse(swap(self.db, self.chip, self.helper, 29.5))
        self.assertIn(self.chip_id, self.db.blocked)

    def test_capacity_rollback_flagged(self):
        self.assertTrue(swap(self.db, self.chip, self.helper, 25.0))
        self.assertFalse(swap(self.db, self.chip, self.helper, 30.0))

    def test_response_matches_definition(self):
        nonce = self.db.issue_nonce(self.chip_id)
        resp = self.chip.auth(nonce, self.helper)
        self.assertEqual(resp, response(self.db.hsm[self.chip_id], nonce, self.chip_id))


if __name__ == "__main__":
    unittest.main(verbosity=2)
