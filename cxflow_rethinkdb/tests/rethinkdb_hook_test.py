import json
from os import path

import rethinkdb as r

from cxflow.tests.test_core import CXTestCaseWithDir
from cxflow_rethinkdb import RethinkDBHook
from cxflow_rethinkdb.utils import create_db, create_table, select_by_id

HOST = 'localhost'
PORT = 28015
USER = 'admin'
PASSWORD = ''
DB = 'rethinktest'
TABLE = 'tabletest'

CONFIG = {'a': 'b', 'c': ['d', 'e']}


class RethinkDBHookTest(CXTestCaseWithDir):
    """
    RethinkDB hook test.

    RethinkDB must run and be accessible as described in the configuration above.

    Example of docker run:
    $ docker run --name test-rethink -p 28015:28015 -d rethinkdb
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._credentials = {
            'host': HOST,
            'port': PORT,
            'user': USER,
            'password': PASSWORD
        }

        self._credentials_file = 'rethink_credentials.json'

    def setUp(self):
        """Save credentials and config to respective files and set up the database."""
        super().setUp()

        create_db(credentials=self._credentials, db_name=DB)
        create_table(credentials=self._credentials, db_name=DB, table_name=TABLE)

        with open(path.join(self.tmpdir, self._credentials_file), 'w') as cred_f:
            json.dump(self._credentials, cred_f)

        with open(path.join(self.tmpdir, 'config.yaml'), 'w') as config_f:
            json.dump(CONFIG, config_f)

    def tearDown(self):
        """Clean the database."""
        super().tearDown()

        with r.connect(**self._credentials) as conn:
            r.db(DB).table_drop(TABLE).run(conn)
            r.db_drop(DB).run(conn)

    def _create_hook(self, rethink_key_file):
        """Create the hook."""
        return RethinkDBHook(output_dir=self.tmpdir, credentials_file=path.join(self.tmpdir, self._credentials_file),
                             db=DB, table=TABLE, rethink_key_file=rethink_key_file)

    def test_id_file(self):
        """Test the document id is correctly dumped."""

        rethink_key_file = 'rethink_key.json'
        hook = self._create_hook(rethink_key_file=rethink_key_file)
        with open(path.join(self.tmpdir, rethink_key_file), 'r') as key_file:
            stored_id = key_file.read()

        self.assertEqual('{"rethink_id": "' + hook._rethink_id + '"}', stored_id)

    def test_epochs(self):
        """Test saving the epoch data."""

        rethink_key_file = 'rethink_key.json'
        hook = self._create_hook(rethink_key_file=rethink_key_file)
        hook.after_epoch(epoch_id=0, epoch_data={'aa': [1,2,3,4], 'bb': [5,6,7,8]})
        hook.after_epoch(epoch_id=1, epoch_data={'aa': [9,0,1,2], 'bb': [3,4,5,6]})

        document = select_by_id(credentials=self._credentials, db_name=DB, table_name=TABLE, doc_id=hook._rethink_id)

        self.assertTrue('config' in document)
        self.assertTrue('timestamp' in document)
        self.assertTrue('id' in document)
        self.assertTrue('training' in document)

        self.assertEqual(document['id'], hook._rethink_id)
        self.assertDictContainsSubset(CONFIG, document['config'])  # dont care about timestamp
        self.assertDictContainsSubset({'epoch_data': {'aa': [1,2,3,4], 'bb': [5,6,7,8]}, 'epoch_id': 0}, document['training'][0])
        self.assertDictContainsSubset({'epoch_data': {'aa': [9,0,1,2], 'bb': [3,4,5,6]}, 'epoch_id': 1}, document['training'][1])
