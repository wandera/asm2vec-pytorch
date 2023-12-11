from os import path
from unittest import TestCase

from asm2vec import __data__
from asm2vec.tensors import save_partial_tensors


class TestTensors(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("\n--- TestTensors ---")
        cls.data_path = path.join(__data__, "partial_tensors/")

    def test_save_partial_tensors(self):
        """Calculates the average of tensors with the same SHA1 prefix, saves it in a separate tensors
        and returns list of files in the directory"""
        expected_tensor_list = ['34cdc8fb7b23b5a66d953d8e76a1d77d520c0d69',
                                '129d99db0085b124617b3fc355daccf84e92c19c']
        self.assertEqual(save_partial_tensors(self.data_path), expected_tensor_list)
