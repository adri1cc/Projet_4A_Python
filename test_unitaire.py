import unittest

import strategies

class TestSMA(unittest.TestCase):
    def test_SMA_is_instance_of_SimpleSMA(self):
        s = strategies.SimpleSMALive("BTC/USDT","2023-06_06", 20)
        self.assertIsInstance(s, strategies.SimpleSMALive)

if __name__ == '__main__':
    unittest.main()