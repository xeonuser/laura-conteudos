"""Run with the desktop environment: python -m unittest discover -s tests -p test_desktop.py."""
import json
import tempfile
import unittest
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication
    from desktop.app import Library
except ImportError:
    QApplication = None


@unittest.skipUnless(QApplication, 'Instale desktop/requirements.txt para testar o aplicativo nativo')
class LibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'state.json'
        self.library = Library(self.path)

    def test_favorites_and_resume_survive_restart(self):
        self.library.toggleFavorite('bunny')
        self.library.progress('bunny', 12000, 50000)
        restored = Library(self.path)
        self.assertTrue(restored.items[0]['favorite'])
        self.assertEqual(restored.items[0]['position'], 12000)
        restored.progress('bunny', 50000, 50000)
        self.assertEqual(restored.items[0]['position'], 0)

    def test_local_import_deduplicates_and_reset_preserves_file(self):
        video = Path(self.directory.name) / 'Meu filme.mp4'
        video.write_bytes(b'example')
        item = Library.local_item(video)
        self.library._finish_scan([item], '')
        self.library._finish_scan([item], '')
        self.assertEqual(len(self.library.items), 3)
        self.assertTrue(self.library.items[-1]['url'].startswith('file:'))
        self.library.reset()
        self.assertTrue(video.exists())
        self.assertEqual(len(self.library.items), 2)

    def test_corrupt_state_recovers(self):
        self.path.write_text('not json')
        restored = Library(self.path)
        self.assertEqual(len(restored.items), 2)
