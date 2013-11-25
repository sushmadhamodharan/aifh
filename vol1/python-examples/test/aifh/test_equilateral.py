__author__ = 'jheaton'

# General-purpose Python library imports
import os
import sys
import unittest


# Find the AIFH core files
aifh_dir = os.path.dirname(os.path.abspath(__file__))
aifh_dir = os.path.abspath(aifh_dir + os.sep + ".." + os.sep + ".." + os.sep + "lib" + os.sep + "aifh")
sys.path.append(aifh_dir)

from equilateral import Equilateral
from scipy.spatial import distance


class TestEquilateral(unittest.TestCase):
    def test_equilateral(self):
        eq = Equilateral(3, -1, 1)
        d = eq.encode(1);
        self.assertAlmostEqual(0.8660254037844386, d[0], 7)
        self.assertAlmostEqual(-0.5, d[1], 7)

    def test_decode(self):
        eq = Equilateral(3, -1, 1)
        d0 = [0.866, 0.5]
        d1 = [-0.866, 0.5]
        d2 = [0, -1]
        self.assertEqual(2, eq.decode(d0))
        self.assertEqual(2, eq.decode(d1))
        self.assertEqual(0, eq.decode(d2))

    def test_all_equal(self):
        eq = Equilateral(10, -1, 1)
        compare_dist = -1

        for x in range(0, 10):
            base_class = eq.encode(x)
            for y in range(0, 10):
                if x != y:
                    otherClass = eq.encode(y)
                    dist = distance.euclidean(base_class, otherClass)
                    if compare_dist < 0:
                        compare_dist = dist
                    else:
                        self.assertAlmostEqual(dist, compare_dist, 7)

