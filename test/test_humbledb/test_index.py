
import mock
import pymongo

from ..util import *
from humbledb import Document, Embed, Index


def teardown():
    DBTest.connection.drop_database(database_name())


class DocTest(Document):
    config_database = database_name()
    config_collection = 'test'

    user_name = 'u'


def test_index_basic():
    class Test(Document):
        config_database = database_name()
        config_collection = 'test'
        config_indexes = [Index('user_name')]

        user_name = 'u'

    with DBTest:
        with mock.patch.object(Test, 'collection') as coll:
            coll.find_one.__name__ = 'find_one'
            Test._ensured = None
            Test.find_one()
            coll.ensure_index.assert_called_with(
                    Test.user_name,
                    background=True,
                    cache_for=60*60*24)


def test_index_basic_sparse():
    class Test(Document):
        config_database = database_name()
        config_collection = 'test'
        config_indexes = [Index('user_name', sparse=True)]

        user_name = 'u'

    with DBTest:
        with mock.patch.object(Test, 'collection') as coll:
            coll.find_one.__name__ = 'find_one'
            Test._ensured = None
            Test.find_one()
            coll.ensure_index.assert_called_with(
                    Test.user_name,
                    background=True,
                    cache_for=60*60*24,
                    sparse=True)


def test_index_basic_directional():
    class Test(Document):
        config_database = database_name()
        config_collection = 'test'
        config_indexes = [Index([('user_name', pymongo.DESCENDING)])]

        user_name = 'u'

    with DBTest:
        with mock.patch.object(Test, 'collection') as coll:
            coll.find_one.__name__ = 'find_one'
            Test._ensured = None
            Test.find_one()
            coll.ensure_index.assert_called_with(
                    [(Test.user_name, pymongo.DESCENDING)],
                    background=True,
                    cache_for=60*60*24)


def test_index_override_defaults():
    class Test(Document):
        config_database = database_name()
        config_collection = 'test'
        config_indexes = [Index('user_name', background=False, cache_for=60)]

        user_name = 'u'

    with DBTest:
        with mock.patch.object(Test, 'collection') as coll:
            coll.find_one.__name__ = 'find_one'
            Test._ensured = None
            Test.find_one()
            coll.ensure_index.assert_called_with(
                    Test.user_name,
                    background=False,
                    cache_for=60)


def test_resolve_dotted_index():
    class TestResolveIndex(DocTest):
        meta = Embed('m')
        meta.tag = 't'

    eq_(Index('')._resolve_index(TestResolveIndex, 'meta'), 'm')
    eq_(Index('')._resolve_index(TestResolveIndex, 'meta.tag'), 'm.t')
    eq_(Index('')._resolve_index(TestResolveIndex, 'meta.foo'), 'meta.foo')


def test_resolve_deep_dotted_index():
    class TestResolveIndex(DocTest):
        meta = Embed('m')
        meta.deep = Embed('d')
        meta.deep.deeper = Embed('d')
        meta.deep.deeper.deeper_still = Embed('d')
        meta.deep.deeper.deeper_still.tag = 't'

    eq_(Index('')._resolve_index(TestResolveIndex, 'meta.deep'), 'm.d')
    eq_(Index('')._resolve_index(TestResolveIndex, 'meta.deep.deeper'),
            'm.d.d')
    eq_(Index('')._resolve_index(TestResolveIndex,
        'meta.deep.deeper.deeper_still'), 'm.d.d.d')
    eq_(Index('')._resolve_index(TestResolveIndex,
        'meta.deep.deeper.deeper_still.tag'), 'm.d.d.d.t')


def test_resolve_compound_index():
    class Test(Document):
        config_database = database_name()
        config_collection = 'test'
        config_indexes = [Index([('user_name', pymongo.ASCENDING), ('compound',
            pymongo.DESCENDING)])]

        user_name = 'u'
        compound = 'c'

    with DBTest:
        # This will raise a TypeError
        with mock.patch.object(Test, 'collection') as coll:
            coll.find_one.__name__ = 'find_one'
            Test._ensured = None
            Test.find_one()
            coll.ensure_index.assert_called_with(
                    [(Test.user_name, pymongo.ASCENDING), (Test.compound,
                        pymongo.DESCENDING)],
                    background=True,
                    cache_for=60*60*24)



@raises(TypeError)
def test_resolve_non_string_attribute_fails():
    class Test(Document):
        config_database = database_name()
        config_collection = 'test'
        config_indexes = [Index('value')]

        value = True

    with DBTest:
        # This will raise a TypeError
        with mock.patch.object(Test, 'collection') as coll:
            coll.find_one.__name__ = 'find_one'
            Test._ensured = None
            Test.find_one()
            coll.ensure_index.assert_not_called()

@raises(TypeError)
def test_badly_formed_index_raises_error():
    class Test(Document):
        config_database = database_name()
        config_collection = 'test'
        config_indexes = [Index([('value',)])]

    with DBTest:
        # This will raise a TypeError
        with mock.patch.object(Test, 'collection') as coll:
            coll.find_one.__name__ = 'find_one'
            Test._ensured = None
            Test.find_one()
            coll.ensure_index.assert_not_called()

