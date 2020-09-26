import os
import tempfile
import unittest

from ..context import zoia
import zoia.backend.config
import zoia.backend.json


class ZoiaUnitTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        library_root = os.path.join(self.tmpdir.name, 'library')
        os.mkdir(library_root)

        db_root = os.path.join(self.tmpdir.name, 'metadata')
        os.mkdir(db_root)

        self.config = zoia.backend.config.ZoiaConfig(
            library_root=library_root,
            db_root=db_root,
            backend=zoia.backend.config.ZoiaBackend.JSON,
        )

        self.metadata = zoia.backend.json.JSONMetadata(self.config)

    def tearDown(self):
        self.tmpdir.cleanup()
