import os
from os import path
from unittest import TestCase

from asm2vec import __data__
from asm2vec.tensors import move_files, save_partial_tensors


class TestTensors(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print("\n--- TestTensors ---")
        cls.data_path = path.join(__data__, "partial_tensors/")
        cls.assembly_path = __data__

    def test_move_files(self):
        limit = 2
        binary_dir = "129d99db0085b124617b3fc355daccf84e92c19c"
        assembly_dirs = ['129d99db0085b124617b3fc355daccf84e92c19c_0',
                         '129d99db0085b124617b3fc355daccf84e92c19c_1',
                         '129d99db0085b124617b3fc355daccf84e92c19c_2']
        expected_assembly_dirs = [os.path.abspath(os.path.join(self.assembly_path, x)) for x in assembly_dirs]
        print(expected_assembly_dirs)
        self.assertEqual(
            move_files(os.path.join(self.assembly_path, binary_dir), limit), expected_assembly_dirs)

    def test_save_partial_tensors(self):
        """Calculates the average of tensors with the same SHA1 prefix, saves it in a separate tensors
        and returns list of files in the directory"""
        expected_tensor_list = ['129d99db0085b124617b3fc355daccf84e92c19c',
                                '34cdc8fb7b23b5a66d953d8e76a1d77d520c0d69']
        self.assertEqual(save_partial_tensors(self.data_path), expected_tensor_list)
