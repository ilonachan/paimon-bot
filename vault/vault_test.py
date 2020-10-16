import unittest
from vault import vault, vault_init, vault_ready


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(vault_ready(), False)
        self.assertEqual(vault.test('test'), 'test')
        self.assertEqual(vault_init('bruh'), True)
        self.assertEqual(vault_ready(), True)
        self.assertEqual(vault.test('abc'), 'test')
        self.assertEqual(vault.not_existent('test'), 'test')


if __name__ == '__main__':
    unittest.main()
