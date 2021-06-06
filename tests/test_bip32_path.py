# Copyright (c) 2020 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# Imports
import binascii
import unittest
from bip_utils import Bip32, Bip32PathError, Bip32PathParser, Bip32Utils

# Tests for paths
TEST_VECT_PATH = [
    {
        "path": "m",
        "parsed": [],
        "to_str": "",
    },
    {
        "path": "m/",
        "parsed": [],
        "to_str": "",
    },
    {
        "path": "m/  0/1",
        "parsed": [0, 1],
        "to_str": "0/1",
    },
    {
        "path": "m/0  /1'",
        "parsed": [0, Bip32Utils.HardenIndex(1)],
        "to_str": "0/1'",
    },
    {
        "path": "m/0  /1p",
        "parsed": [0, Bip32Utils.HardenIndex(1)],
        "to_str": "0/1'",
    },
    {
        "path": "m/0'/1'/2/",
        "parsed": [Bip32Utils.HardenIndex(0), Bip32Utils.HardenIndex(1), 2],
        "to_str": "0'/1'/2",
    },
    {
        "path": "m/0p/1p/2/",
        "parsed": [Bip32Utils.HardenIndex(0), Bip32Utils.HardenIndex(1), 2],
        "to_str": "0'/1'/2",
    },
    {
        "path": "0",
        "parsed": [0],
        "to_str": "0",
    },
    {
        "path": "0/",
        "parsed": [0],
        "to_str": "0",
    },
    {
        "path": "0'/1'/2",
        "parsed": [Bip32Utils.HardenIndex(0), Bip32Utils.HardenIndex(1), 2],
        "to_str": "0'/1'/2",
    },
    {
        "path": "0p/1p/2",
        "parsed": [Bip32Utils.HardenIndex(0), Bip32Utils.HardenIndex(1), 2],
        "to_str": "0'/1'/2",
    },
]

# Tests for invalid paths
TEST_VECT_PATH_INVALID = [
    "",
    "mm",
    "m//",
    "n/",
    "mm/0",
    "m/0''",
    "m/0pp",
    "m/0'0/1",
    "m/0p0/1",
    "m/a/1",
    "m/0 1/1",
    "m/0//1/1",
    "0/a/1",
    "0//1/1",
]


#
# Bip32 path tests
#
class Bip32PathTests(unittest.TestCase):
    # Run all tests in test vector
    def test_vector(self):
        for test in TEST_VECT_PATH:
            path = Bip32PathParser.Parse(test["path"])

            # Check if valid
            self.assertTrue(path.IsValid())
            # Check length
            self.assertEqual(len(test["parsed"]), path.Length())
            # Check string conversion
            self.assertEqual(test["to_str"], path.ToStr())
            self.assertEqual(test["to_str"], str(path))

            # Check by iterating
            for idx, elem in enumerate(path):
                test_elem = test["parsed"][idx]

                self.assertEqual(test_elem, int(elem))
                self.assertEqual(test_elem, int(path[idx]))
                self.assertEqual(test_elem, elem.ToInt())
                self.assertEqual(Bip32Utils.IsHardenedIndex(test_elem), elem.IsHardened())
                self.assertTrue(elem.IsValid())
            # Check by converting to list
            for idx, elem in enumerate(path.ToList()):
                self.assertEqual(test["parsed"][idx], elem)

    # Test invalid paths
    def test_invalid_paths(self):
        seed = binascii.unhexlify(b"000102030405060708090a0b0c0d0e0f")

        for test in TEST_VECT_PATH_INVALID:
            path = Bip32PathParser.Parse(test)

            # Check if not valid
            self.assertFalse(path.IsValid())
            # Check conversion to string
            self.assertEqual("", path.ToStr())
            self.assertEqual("", str(path))
            # Check conversion to list
            self.assertEqual([], path.ToList())

            # Try to derive an invalid path
            bip32 = Bip32.FromSeed(seed)
            self.assertRaises(Bip32PathError, bip32.DerivePath, test)
            self.assertRaises(Bip32PathError, Bip32.FromSeedAndPath, seed, test)