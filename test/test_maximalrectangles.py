import sys
import unittest


from greedypacker import maximal_rectangles
from greedypacker import item
from .base import BaseTestCase
from .util import stdout_redirect


class StaticMethods(BaseTestCase):
    def setUp(self):
        self.M = maximal_rectangles.MaximalRectangle(0, 0)


    def tearDown(self):
        del self.M


    def testItemFitsRect(self):
        """
        Single Item Fits the FreeRectangle
        Rotation == False
        """
        I = item.Item(2, 4)
        F = maximal_rectangles.FreeRectangle(2, 4, 0 ,0)

        self.assertTrue(self.M.item_fits_rect(I, F))


    def testItemDoesntFitsRect(self):
        """
        Single Item Fits the FreeRectangle
        Rotation == False
        """
        I = item.Item(2, 4)
        F = maximal_rectangles.FreeRectangle(2, 3, 0, 0)

        self.assertFalse(self.M.item_fits_rect(I, F))

    
    def testSplitRectangle(self):
        """
        Split a rectangle into two maximal rectangles
        """
        I = item.Item(2,2)
        F = maximal_rectangles.FreeRectangle(4, 4, 0, 0)
        
        Ft = maximal_rectangles.FreeRectangle(4, 2, 0, 2)
        Fr = maximal_rectangles.FreeRectangle(2, 4, 2, 0)

        remainders = self.M.split_rectangle(F, I)
        self.assertCountEqual(remainders, [Ft, Fr])
        

    def testCheckIntersectionTrue(self):
        """
        Two items with partial overlap
        """
        F0 = maximal_rectangles.FreeRectangle(4, 4, 0, 0)
        B = (0, 0, 2, 2)
        self.assertTrue(self.M.checkInstersection(F0, B))


    def testCheckIntersectionFalse(self):
        """
        Two items with no overlap
        """
        F0 = maximal_rectangles.FreeRectangle(4, 4, 0, 0)
        B = (5, 0, 9, 2)
        self.assertFalse(self.M.checkInstersection(F0, B))


    def testItemBounds(self):
        """
        Returns the bounding box for an item
        """
        I = item.Item(4, 2, [2,1])
        self.assertEqual(self.M.item_bounds(I), (2, 1, 6, 3))
    

    def testFindOverlap(self):
        """
        Returns the area of overlap of two
        intersected rectangles
        """
        F0 = maximal_rectangles.FreeRectangle(4, 4, 0, 0)
        F1 = maximal_rectangles.FreeRectangle(4, 2, 3, 0)
        B = (3, 0, 7, 2)

        self.assertEqual(self.M.findOverlap(F0, B), (3, 0, 4, 2))


    def testClipOverlap(self):
        """
        Returns maximal rectangle remainders of a rectangle
        fully overlapping a bounding box
        """
        F0 = maximal_rectangles.FreeRectangle(3, 3, 0, 0)
        F1 = maximal_rectangles.FreeRectangle(1, 1, 1, 1)
        B = (1, 1, 2, 2)
    
        overlap = self.M.findOverlap(F0, B)
        remainders = self.M.clipOverlap(F0, overlap)

        Fl = maximal_rectangles.FreeRectangle(1, 3, 0, 0)
        Fr = maximal_rectangles.FreeRectangle(1, 3, 2, 0)
        Fb = maximal_rectangles.FreeRectangle(3, 1, 0, 0)
        Ft = maximal_rectangles.FreeRectangle(3, 1, 0, 2)

        self.assertCountEqual(remainders, [Fl, Fr, Fb, Ft])
        

    def testEncapsulates(self):
        """
        Returns a boolean if the second rectangle
        is fully encapsulated in the first
        """
        F0 = maximal_rectangles.FreeRectangle(3, 3, 0, 0)
        F1 = maximal_rectangles.FreeRectangle(1, 1, 1, 1)
        F2 = maximal_rectangles.FreeRectangle(2, 1, 5, 1)

        with self.subTest():
            self.assertTrue(self.M.encapsulates(F0, F1))
        with self.subTest():
            self.assertFalse(self.M.encapsulates(F0, F2))


    def testRemoveRedundent(self):
        """
        F1 should be removed from freerects
        """
        F0 = maximal_rectangles.FreeRectangle(3, 3, 0, 0)
        F1 = maximal_rectangles.FreeRectangle(1, 1, 1, 1)
        F2 = maximal_rectangles.FreeRectangle(2, 1, 5, 1)
        F3 = maximal_rectangles.FreeRectangle(1, 1, 5, 1)
        self.M.freerects = [F0, F1, F2, F3]
        self.M.remove_redundent()
        self.assertCountEqual(self.M.freerects, [F0, F2])


    def testPruneOverlaps(self):
        F0 = maximal_rectangles.FreeRectangle(4, 4, 0, 0)
        F1 = maximal_rectangles.FreeRectangle(1, 1, 0, 0)
        self.M.freerects = [F0, F1]
        itemBounds = (0, 0, 2, 2)
        self.M.prune_overlaps(itemBounds)
        
        F2 = maximal_rectangles.FreeRectangle(2, 4, 2, 0)
        F3 = maximal_rectangles.FreeRectangle(4, 2, 0, 2)
        self.assertCountEqual(self.M.freerects, [F2, F3])


class FirstFit(BaseTestCase):
    def setUp(self):
        self.M = maximal_rectangles.MaximalRectangle(4, 4)


    def tearDown(self):
        del self.M


    def testSingleItemInsert(self):
        """
        Single Item insertion checks for maximal
        rectangles result
        """
        I = item.Item(2, 2)
        F0 = maximal_rectangles.FreeRectangle(2, 4, 2, 0)
        F1 = maximal_rectangles.FreeRectangle(4, 2, 0, 2)
        self.M.first_fit(I)
        self.assertCountEqual(self.M.freerects, [F0, F1])


    def testTwoItemInsert(self):
        """
        Two Item insertion checks for maximal
        rectangles result
        """
        I = item.Item(2, 2)
        I2 = item.Item(4, 2)
        self.M.first_fit(I)
        self.M.first_fit(I2)
        F0 = maximal_rectangles.FreeRectangle(2, 2, 2, 0)
        self.assertEqual(self.M.freerects, [F0])


class BestArea(BaseTestCase):
    def setUp(self):
        self.M = maximal_rectangles.MaximalRectangle(8, 4)


    def tearDown(self):
        del self.M


    def testBadInsert(self):
        """
        Item too Big
        Rotation = False
        """
        I = item.Item(9, 4)
        F0 = maximal_rectangles.FreeRectangle(8, 4, 0, 0)
        self.M.best_area(I)
        self.assertCountEqual(self.M.freerects, [F0])

    def testTwoItemInsert(self):
        """
        Two Item insertion 
        Rotation = False
        """
        I = item.Item(2, 2)
        I2 = item.Item(4, 2)
        F0 = maximal_rectangles.FreeRectangle(6, 2, 2, 0)
        F1 = maximal_rectangles.FreeRectangle(4, 4, 4, 0)
        self.M.best_area(I)
        self.M.best_area(I2)
        with self.subTest():
            self.assertCountEqual(self.M.freerects, [F0, F1])
        with self.subTest():
            self.assertEqual(I.CornerPoint, (0,0))
        with self.subTest():
            self.assertEqual(I2.CornerPoint, (0,2))


class BestShortside(BaseTestCase):
    def setUp(self):
        self.M = maximal_rectangles.MaximalRectangle(8, 4)


    def tearDown(self):
        del self.M


    def testBadInsert(self):
        """
        Item too Big
        Rotation = False
        """
        I = item.Item(9, 4)
        F0 = maximal_rectangles.FreeRectangle(8, 4, 0, 0)
        self.M.best_shortside(I)
        self.assertCountEqual(self.M.freerects, [F0])

    def testTwoItemInsert(self):
        """
        Two Item insertion 
        Rotation = False
        """
        I = item.Item(1, 1)
        I2 = item.Item(2, 2)
        F0 = maximal_rectangles.FreeRectangle(7, 1, 1, 0)
        F1 = maximal_rectangles.FreeRectangle(8, 1, 0, 3)
        F2 = maximal_rectangles.FreeRectangle(6, 4, 2, 0)
        self.M.best_shortside(I)
        self.M.best_shortside(I2)
        with self.subTest():
            self.assertCountEqual(self.M.freerects, [F0, F1, F2])
        with self.subTest():
            self.assertEqual(I.CornerPoint, (0,0))
        with self.subTest():
            self.assertEqual(I2.CornerPoint, (0,1))


class BestLongside(BaseTestCase):
    def setUp(self):
        self.M = maximal_rectangles.MaximalRectangle(8, 4)


    def tearDown(self):
        del self.M


    def testBadInsert(self):
        """
        Item too Big
        Rotation = False
        """
        I = item.Item(9, 4)
        F0 = maximal_rectangles.FreeRectangle(8, 4, 0, 0)
        self.M.best_shortside(I)
        self.assertCountEqual(self.M.freerects, [F0])

    def testTwoItemInsert(self):
        """
        Two Item insertion 
        Rotation = False
        """
        I = item.Item(1, 1)
        I2 = item.Item(2, 2)
        F0 = maximal_rectangles.FreeRectangle(5, 4, 3, 0)
        F1 = maximal_rectangles.FreeRectangle(1, 3, 0, 1)
        F2 = maximal_rectangles.FreeRectangle(8, 2, 0, 2)
        self.M.best_longside(I)
        self.M.best_longside(I2)
        with self.subTest():
            self.assertCountEqual(self.M.freerects, [F0, F1, F2])
        with self.subTest():
            self.assertEqual(I.CornerPoint, (0,0))
        with self.subTest():
            self.assertEqual(I2.CornerPoint, (1,0))


class BestBottomLeft(BaseTestCase):
    def setUp(self):
        self.M = maximal_rectangles.MaximalRectangle(8, 4)


    def tearDown(self):
        del self.M


    def testBadInsert(self):
        """
        Item too Big
        Rotation = False
        """
        I = item.Item(9, 4)
        F0 = maximal_rectangles.FreeRectangle(8, 4, 0, 0)
        self.M.best_shortside(I)
        self.assertCountEqual(self.M.freerects, [F0])

    def testThreeItemInsert(self):
        """
        Three Item insertion 
        Rotation = False
        """
        I = item.Item(4, 1)
        I2 = item.Item(4, 2)
        I3 = item.Item(1, 1)
        F0 = maximal_rectangles.FreeRectangle(8, 2, 0, 2)
        F1 = maximal_rectangles.FreeRectangle(3, 3, 1, 1)
        self.M.best_bottomleft(I)
        self.M.best_bottomleft(I2)
        self.M.best_bottomleft(I3)
        with self.subTest():
            self.assertCountEqual(self.M.freerects, [F0, F1])
        with self.subTest():
            self.assertEqual(I.CornerPoint, (0,0))
        with self.subTest():
            self.assertEqual(I2.CornerPoint, (4,0))
        with self.subTest():
            self.assertEqual(I3.CornerPoint, (0,1))


class ContactPoint(BaseTestCase):
    def setUp(self):
        self.M = maximal_rectangles.MaximalRectangle(8, 4)


    def tearDown(self):
        del self.M


    def testBadInsert(self):
        """
        Item too Big
        Rotation = False
        """
        I = item.Item(9, 4)
        F0 = maximal_rectangles.FreeRectangle(8, 4, 0, 0)
        self.M.best_shortside(I)
        self.assertCountEqual(self.M.freerects, [F0])

    def testThreeItemInsert(self):
        """
        Three Item insertion 
        Rotation = False
        """
        I = item.Item(1, 1)
        I2 = item.Item(4, 2)
        I3 = item.Item(1, 1)
        F0 = maximal_rectangles.FreeRectangle(8, 2, 0, 2)
        F1 = maximal_rectangles.FreeRectangle(3, 4, 5, 0)
        self.M.contact_point(I)
        self.M.contact_point(I2)
        self.M.contact_point(I3)
        with self.subTest():
            self.assertCountEqual(self.M.freerects, [F0, F1])
        with self.subTest():
            self.assertEqual(I.CornerPoint, (0,0))
        with self.subTest():
            self.assertEqual(I2.CornerPoint, (1,0))
        with self.subTest():
            self.assertEqual(I3.CornerPoint, (0,1))


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    if pattern is None:
        suite.addTests(loader.loadTestsFromTestCase(StaticMethods))
        suite.addTests(loader.loadTestsFromTestCase(FirstFit))
        suite.addTests(loader.loadTestsFromTestCase(BestArea))
        suite.addTests(loader.loadTestsFromTestCase(BestShortside))
        suite.addTests(loader.loadTestsFromTestCase(BestLongside))
        suite.addTests(loader.loadTestsFromTestCase(BestBottomLeft))
        suite.addTests(loader.loadTestsFromTestCase(ContactPoint))
    else:
        tests = loader.loadTestsFromName(pattern,
                                         module=sys.modules[__name__])
        failedTests = [t for t in tests._tests
                       if type(t) == unittest.loader._FailedTest]
        if len(failedTests) == 0:
            suite.addTests(tests)
    return suite