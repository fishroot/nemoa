# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.base.file'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from configparser import ConfigParser
import tempfile
from pathlib import Path
import numpy as np
from nemoa.base.file import binfile, csvfile, inifile, textfile
from nemoa.test import ModuleTestCase

class TestBinfile(ModuleTestCase):
    """Testcase for the module nemoa.base.file.binfile."""

    module = 'nemoa.base.file.binfile'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.gz')
        self.data = b'eJxrYK4tZDoiGBkGT0ZqotZJzt3/AbFpXoAgyI=='
        binfile.save(self.data, self.filepath)

    def test_openx(self) -> None:
        filepath = Path(tempfile.NamedTemporaryFile().name)
        with self.subTest(file=filepath):
            with binfile.openx(filepath, mode='w') as fh:
                fh.write(self.data)
            if filepath.is_file():
                with binfile.openx(filepath, mode='r') as fh:
                    data = fh.read()
                filepath.unlink()
                self.assertTrue(data == self.data)
        file = filepath.open(mode='wb')
        with self.subTest(file=file):
            with binfile.openx(file, mode='w') as fh:
                fh.write(self.data)
            if not file.closed:
                file.close()
                file = filepath.open(mode='rb')
                with binfile.openx(file, mode='r') as fh:
                    data = fh.read()
                if not file.closed:
                    file.close()
                    self.assertTrue(data == self.data)

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_load(self) -> None:
        data = binfile.load(self.filepath)
        self.assertEqual(data, self.data)

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()

class TestTextfile(ModuleTestCase):
    """Testcase for the module nemoa.base.file.textfile."""

    module = 'nemoa.base.file.textfile'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.txt')
        self.header = "-*- coding: utf-8 -*-"
        self.content = ['first line', 'second line']
        self.text = f"# {self.header}\n\n" + '\n'.join(self.content)
        textfile.save(self.text, self.filepath)

    def test_openx(self) -> None:
        filepath = Path(tempfile.NamedTemporaryFile().name + '.txt')
        with self.subTest(file=filepath):
            with textfile.openx(filepath, mode='w') as fh:
                fh.write(self.text)
            if filepath.is_file():
                with textfile.openx(filepath, mode='r') as fh:
                    text = fh.read()
                filepath.unlink()
                self.assertTrue(text == self.text)
        file = filepath.open(mode='w')
        with self.subTest(file=file):
            with textfile.openx(file, mode='w') as fh:
                fh.write(self.text)
            if not file.closed:
                file.close()
                file = filepath.open(mode='r')
                with textfile.openx(file, mode='r') as fh:
                    text = fh.read()
                if not file.closed:
                    file.close()
                    self.assertTrue(text == self.text)

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_load(self) -> None:
        text = textfile.load(self.filepath)
        self.assertEqual(text, self.text)

    def test_get_header(self) -> None:
        header = textfile.get_header(self.filepath)
        self.assertEqual(header, self.header)

    def test_get_content(self) -> None:
        content = textfile.get_content(self.filepath)
        self.assertEqual(content, self.content)

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()

class TestCsvfile(ModuleTestCase):
    """Testcase for the module nemoa.base.file.csvfile."""

    module = 'nemoa.base.file.csvfile'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.csv')
        self.header = '-*- coding: utf-8 -*-'
        self.data = np.array(
            [('row1', 1.1, 1.2), ('row2', 2.1, 2.2), ('row3', 3.1, 3.2)],
            dtype=[('label', 'U8'), ('col1', 'f8'), ('col2', 'f8')])
        self.delim = ','
        self.colnames = ['', 'col1', 'col2']
        self.rownames = list(self.data['label'].flat)
        csvfile.save(
            self.filepath, self.data, header=self.header, labels=self.colnames,
            delim=self.delim)
        self.file = csvfile.CSVFile(self.filepath)

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_header(self) -> None:
        self.assertEqual(self.file.header, self.header)

    def test_delim(self) -> None:
        self.assertEqual(self.file.delim, self.delim)

    def test_format(self) -> None:
        self.assertEqual(self.file.format, csvfile.FORMAT_STANDARD)

    def test_colnames(self) -> None:
        self.assertEqual(self.file.colnames, self.colnames)

    def test_rownames(self) -> None:
        self.assertEqual(self.file.rownames, self.rownames)

    def test_labelid(self) -> None:
        self.assertEqual(self.file.labelid, 0)

    # def test_load(self) -> None:
    #     data = csvfile.load(self.filepath)
    #     self.assertTrue(isinstance(data, np.ndarray))
    #     col1 = np.array(data)['col1']
    #     self.assertTrue(np.all(col1 == self.data['col1']))
    #     col2 = np.array(data)['col2']
    #     self.assertTrue(np.all(col2 == self.data['col2']))

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()

class TestInifile(ModuleTestCase):
    """Testcase for the module nemoa.base.file.inifile."""

    module = 'nemoa.base.file.inifile'

    def setUp(self) -> None:
        self.filepath = Path(tempfile.NamedTemporaryFile().name + '.ini')
        self.header = '-*- coding: utf-8 -*-'
        self.obj = {
            'n': {'a': 's', 'b': True, 'c': 1},
            'l1': {'a': 1}, 'l2': {'a': 2}}
        self.structure = {
            'n': {'a': 'str', 'b': 'bool', 'c': 'int'},
            'l[0-9]*': {'a': 'int'}}
        self.text = (
            "# -*- coding: utf-8 -*-\n\n"
            "[n]\na = s\nb = True\nc = 1\n\n"
            "[l1]\na = 1\n\n[l2]\na = 2\n\n")
        inifile.save(self.obj, self.filepath, header=self.header)

    def test_parse(self) -> None:
        parser = ConfigParser()
        setattr(parser, 'optionxform', lambda key: key)
        parser.read_string(self.text)
        obj = inifile.parse(parser, structure=self.structure)
        self.assertEqual(obj, self.obj)

    def test_encode(self) -> None:
        text = inifile.encode(self.obj, header=self.header)
        self.assertEqual(text, self.text)

    def test_decode(self) -> None:
        obj = inifile.decode(self.text, structure=self.structure)
        self.assertEqual(obj, self.obj)

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_load(self) -> None:
        obj = inifile.load(self.filepath, structure=self.structure)
        self.assertEqual(obj, self.obj)

    def test_get_header(self) -> None:
        header = inifile.get_header(self.filepath)
        self.assertEqual(header, self.header)

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()