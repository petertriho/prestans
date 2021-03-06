import unittest

from prestans.provider.cache import Base


class CacheBaseUnitTest(unittest.TestCase):

    def test_debug(self):
        base = Base()
        self.assertEqual(base.debug, False)

        base.debug = True
        self.assertEqual(base.debug, True)
