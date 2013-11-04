import unittest
import pymongo

from .. import models
from .. import signals

# MONGODB CONFIG

models.mongodb_database = pymongo.MongoClient().test_database


class TestModel(models.Model):
    _collection = 'testmodel'

    uid = models.Field()
    name = models.Field()


class TestBaseModel(unittest.TestCase):
    def setUp(self):
        models.mongodb_database.testmodel.remove()

    def tearDown(self):
        models.mongodb_database.testmodel.remove()

    def test_save(self):
        model = TestModel()
        model.uid = 1
        model.name = 'Anton'

        model.save()
        saved = model._objects.find_one({'uid': 1})
        self.assertTrue(saved)
        self.assertEqual(saved['name'], 'Anton')

    def test_find(self):
        model = TestModel()
        model._objects.insert({'uid': 1, 'name': 'John'})

        model.find({'uid': 1})
        self.assertEqual(model.name, 'John')
        self.assertEqual(model.uid, 1)

    def test_delete(self):
        model = TestModel()
        model.uid = 1
        model.name = 'Anton'
        model.save()
        self.assertEquals(model._objects.count(), 1)
        model.delete()
        self.assertEquals(model._objects.count(), 0)

    def test_two_instances(self):
        model1 = TestModel()
        model1.uid = 1
        model1.name = 'Anton'

        model2 = TestModel()
        model2.uid = 2
        model2.name = 'John'
        self.assertEquals(model1.uid, 1)
        self.assertEquals(model2.uid, 2)


if __name__ == '__main__':
    unittest.main()
