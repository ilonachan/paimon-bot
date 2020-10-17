import unittest
import os.path
from vault import vault, vault_init, vault_ready


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(vault_ready(), False)
        self.assertEqual(vault.test('test'), 'test')
        self.assertEqual(vault_init('Wrong key'), None)
        self.assertEqual(vault_ready(), False)
        vault_init('Source File not available', override=True)
        self.assertEqual(vault_ready(), os.path.isfile('vault/vault_base.yaml'))


if __name__ == '__main__':
    unittest.main()
