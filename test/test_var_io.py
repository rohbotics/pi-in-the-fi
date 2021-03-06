import unittest
from unittest import mock
import pifi.var_io as var_io
from io import StringIO
import os

class VarIOTests(unittest.TestCase):
    
    def test_good_seen_SSIDs(self):
        f = mock.mock_open(read_data='Foo    \nBar    \n')
        self.assertEqual(['Foo', 'Bar'], var_io.readSeenSSIDs(open=f))

    def test_empty_seen_SSIDs(self):
        f = mock.mock_open(read_data='')
        self.assertEqual([], var_io.readSeenSSIDs(open=f))

    def test_no_newline_seen_SSIDs(self):
        f = mock.mock_open(read_data='Foo')
        self.assertEqual(['Foo'], var_io.readSeenSSIDs(open=f))
        f = mock.mock_open(read_data='Foo\nBar')
        self.assertEqual(['Foo', 'Bar'], var_io.readSeenSSIDs(open=f))

    def test_duplicate_seen_SSIDs(self):
        f = mock.mock_open(read_data='Foo\nFoo\nFoo\n')
        self.assertEqual(['Foo', 'Foo', 'Foo'], var_io.readSeenSSIDs(open=f))

    def test_not_existant_seen_SSIDs(self):
        f = mock.Mock(side_effect=FileNotFoundError('foo'))
        self.assertEqual([], var_io.readSeenSSIDs(open=f))

    def test_error_reading_seen_SSIDs(self):
        f = mock.Mock(side_effect=IOError('foo'))
        with self.assertRaises(IOError):
            var_io.readSeenSSIDs(open=f)

    def test_numerical_as_str_seen_SSIDs(self):
        f = mock.mock_open(read_data='1234\n0.1\n-5\n')
        self.assertIsInstance(var_io.readSeenSSIDs(open=f)[0], str)
        self.assertIsInstance(var_io.readSeenSSIDs(open=f)[1], str)
        self.assertIsInstance(var_io.readSeenSSIDs(open=f)[2], str)

    def test_write_one_SSID(self):
        f = mock.mock_open()
        ed = mock.MagicMock()
        var_io.writeSeenSSIDs(['Foo'], open=f, ensureDir=ed)
        ed.assert_called_once_with(var_io.seen_SSIDs_path)
        self.assertIn(mock.call().write('Foo\n'), f.mock_calls)

    def test_write_empty_SSIDs(self):
        f = mock.mock_open()
        ed = mock.MagicMock()
        var_io.writeSeenSSIDs([], open=f, ensureDir=ed)
        ed.assert_called_once_with(var_io.seen_SSIDs_path)
        self.assertIn(mock.call().truncate(), f.mock_calls)

    def test_write_multiple_SSIDs(self):
        f = mock.mock_open()
        ed = mock.MagicMock()
        var_io.writeSeenSSIDs(['Foo', 'Bar', 'Baz'], open=f, ensureDir=ed)
        ed.assert_called_once_with(var_io.seen_SSIDs_path)
        self.assertIn(mock.call().write('Foo\n'), f.mock_calls)
        self.assertIn(mock.call().write('Bar\n'), f.mock_calls)
        self.assertIn(mock.call().write('Baz\n'), f.mock_calls)

    def test_write_multiple_existing_file_SSIDs(self):
        output = StringIO("Cats\n")
        ed = mock.MagicMock()
        f = mock.Mock(return_value=output)
        output.close = mock.MagicMock()

        var_io.writeSeenSSIDs(['Foo', 'Bar', 'Baz'], open=f, ensureDir=ed)
        ed.assert_called_once_with(var_io.seen_SSIDs_path)

        self.assertNotEqual("Cats\nFoo\nBar\nBaz\n", output.getvalue())
        self.assertEqual("Foo\nBar\nBaz\n", output.getvalue())

    def test_write_multiple_existing_longer_SSIDs(self):
        output = StringIO("Foo\nBar\nBaz\n")
        ed = mock.MagicMock()
        f = mock.Mock(return_value=output)
        output.close = mock.MagicMock()

        var_io.writeSeenSSIDs(['Cats'], open=f, ensureDir=ed)
        ed.assert_called_once_with(var_io.seen_SSIDs_path)

        self.assertNotEqual("Foo\nBar\nBaz\nCats\n", output.getvalue())
        self.assertEqual("Cats\n", output.getvalue())

    def test_non_existant_pending(self):
        f = mock.Mock(side_effect=FileNotFoundError('foo'))
        self.assertEqual([], var_io.readPendingConnections(open=f))

    def test_empty_pending(self):
        f = mock.mock_open(read_data='')
        self.assertEqual([], var_io.readPendingConnections(open=f))

    def test_empty_list_pending(self):
        f = mock.mock_open(read_data='[]')
        self.assertEqual([], var_io.readPendingConnections(open=f))

    def test_non_list_pending(self):
        f = mock.mock_open(read_data='{ "foo" : "bar" }')
        with self.assertRaises(ValueError):
            var_io.readPendingConnections(open=f)

    def test_one_list_pending(self):
        f = mock.mock_open(read_data='[{ "foo" : "bar" }]')
        self.assertEqual([{ 'foo' : 'bar' }], var_io.readPendingConnections(open=f))

    def test_empty_write_pending(self):
        output = StringIO()
        ed = mock.MagicMock()
        f = mock.Mock(return_value=output)
        output.close = mock.MagicMock()

        var_io.writePendingConnections([],  open=f, ensureDir=ed)
        ed.assert_called_once_with(var_io.pending_path)
        self.assertEqual('[]', output.getvalue().strip())

    def test_none_write_pending(self):
        output = StringIO()
        ed = mock.MagicMock()
        f = mock.Mock(return_value=output)
        output.close = mock.MagicMock()

        var_io.writePendingConnections(None,  open=f, ensureDir=ed)
        ed.assert_called_once_with(var_io.pending_path)
        self.assertEqual('[]', output.getvalue().strip())

    def test_one_write_pending(self):
        output = StringIO()
        ed = mock.MagicMock()
        f = mock.Mock(return_value=output)
        output.close = mock.MagicMock()

        var_io.writePendingConnections([{ 'foo' : 'bar' }],  open=f, ensureDir=ed)
        ed.assert_called_once_with(var_io.pending_path)
        self.assertEqual('[{ "foo" : "bar" }]'.replace(" ", ""), 
                         output.getvalue().replace(" ", ""))

    def test_one_write_existing_pending(self):
        output = StringIO('[{ "foo" : "baz" }]')
        ed = mock.MagicMock()
        f = mock.Mock(return_value=output)
        output.close = mock.MagicMock()

        var_io.writePendingConnections([{ 'foo' : 'bar' }],  open=f, ensureDir=ed)
        ed.assert_called_once_with(var_io.pending_path)
        self.assertEqual('[{ "foo" : "bar" }]'.replace(" ", ""), 
                         output.getvalue().replace(" ", ""))

    def test_one_write_existing_longer_pending(self):
        output = StringIO('[{ "foo" : "long words" }, { "bar" : "longer words" }]')
        ed = mock.MagicMock()
        f = mock.Mock(return_value=output)
        output.close = mock.MagicMock()

        var_io.writePendingConnections([{ 'foo' : 'bar' }],  open=f, ensureDir=ed)
        ed.assert_called_once_with(var_io.pending_path)
        self.assertEqual('[{ "foo" : "bar" }]'.replace(" ", ""), 
                         output.getvalue().replace(" ", ""))

    def test_ensure_dir(self):
        var_io.ensureDir('/tmp/pifi/test/foo')
        self.assertTrue(os.path.exists('/tmp/pifi/test/'))
        self.assertTrue(os.path.isdir('/tmp/pifi/test/'))
        self.assertFalse(os.path.exists('/tmp/pifi/test/foo'))
        var_io.ensureDir('/tmp/pifi/test/foo')
        self.assertTrue(os.path.exists('/tmp/pifi/test/'))
        self.assertTrue(os.path.isdir('/tmp/pifi/test/'))
        self.assertFalse(os.path.exists('/tmp/pifi/test/foo'))

        # Cleanup
        os.rmdir('/tmp/pifi/test/') 

def main():
    unittest.main()

if __name__ == '__main__':
    main()
