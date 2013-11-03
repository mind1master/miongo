import unittest

from models import *
from signals import *

class TestModel(Model):
    _collection = 'testmodel'

    uid = Field()
    name = Field()

class TestBaseModel(unittest.TestCase):

    def test_save(self):
        model = TestModel()
        model.uid = 1
        model.name = 'Anton'

        model.save()
        saved = self.mongodb.testmodel.find_one({'uid': 1})
        self.assertTrue(saved)
        self.assertEqual(saved['name'], 'Anton')

    def test_find(self):
        self.mongodb.testmodel.insert({'uid': 1, 'name': 'John'})
        model = TestModel()

        model.find({'uid': 1})
        self.assertEqual(model.name, 'John')
        self.assertEqual(model.uid, 1)

    def test_delete(self):
        model = TestModel()
        model.uid = 1
        model.name = 'Anton'
        model.save()
        self.assertEquals(self.mongodb.testmodel.count(), 1)
        model.delete()
        self.assertEquals(self.mongodb.testmodel.count(), 0)

    def test_two_instances(self):
        model1 = TestModel()
        model1.uid = 1
        model1.name = 'Anton'

        model2 = TestModel()
        model2.uid = 2
        model2.name = 'John'
        self.assertEquals(model1.uid, 1)
        self.assertEquals(model2.uid, 2)

# SIGNAL TESTS

class BaseModel(object):
    def __init__(self):
        self.a = 1
        self.b = 1

    def inc_a(self):
        self.a += 1

class TestModel(BaseModel, SignalEmitterMixin):
    BEFORE_INC = 0
    AFTER_INC = 1
    AVAILABLE_SIGNALS = [BEFORE_INC, AFTER_INC]

    def inc_a(self):
        self.emit_signal(self.BEFORE_INC)
        super(TestModel, self).inc_a()
        self.emit_signal(self.AFTER_INC)


def signal_function_1(signal_type, instance):
    instance.b = 5


def signal_function_2(signal_type, instance):
    instance.a += 1

## TESTS START HERE ##


class TestSignalsForInstance(unittest.TestCase):

    def setUp(self):
        self.model = TestModel()

    def tearDown(self):
        self.model.clear_all_signals()

    def test_model(self):
        self.assertEqual(self.model.a, 1)
        self.assertEqual(self.model.b, 1)
        self.model.inc_a()
        self.assertEqual(self.model.a, 2)
        self.assertEqual(self.model.b, 1)

    def test_connect_to_signal(self):
        self.model.connect_to_signal(self.model.BEFORE_INC, signal_function_1)
        self.assertTrue(signal_function_1 in self.model._get_callbacks_for_signal(self.model.BEFORE_INC))

    def test_disconnect_from_signal(self):
        self.model.connect_to_signal(self.model.BEFORE_INC, signal_function_1)
        self.assertTrue(signal_function_1 in self.model._get_callbacks_for_signal(self.model.BEFORE_INC))
        self.model.disconnect_from_signal(self.model.BEFORE_INC, signal_function_1)
        self.assertFalse(signal_function_1 in self.model._get_callbacks_for_signal(self.model.BEFORE_INC))

    def test_pre_signal_works(self):
        self.model.connect_to_signal(self.model.BEFORE_INC, signal_function_1)
        self.model.inc_a()
        self.assertEqual(self.model.b, 5)

    def test_post_signal_works(self):
        self.model.connect_to_signal(self.model.AFTER_INC, signal_function_2)
        self.model.inc_a()
        self.assertEqual(self.model.a, 3)  # second inc is done by signal_function_2

    def test_both_signals_work(self):
        self.model.connect_to_signal(self.model.BEFORE_INC, signal_function_1)
        self.model.connect_to_signal(self.model.AFTER_INC, signal_function_2)
        self.model.inc_a()
        self.assertEqual(self.model.a, 3)  # second inc is done by signal_function_2
        self.assertEqual(self.model.b, 5)


class TestSignalsForClass(unittest.TestCase):
    """
    The same as TestSignalsForInstance, but signals are attached to class
    """

    def tearDown(self):
        TestModel.clear_all_signals()

    def test_connect_to_signal(self):
        TestModel.connect_to_signal(TestModel.BEFORE_INC, signal_function_1)
        self.assertTrue(signal_function_1 in TestModel._get_callbacks_for_signal(TestModel.BEFORE_INC))

    def test_disconnect_from_signal(self):
        TestModel.connect_to_signal(TestModel.BEFORE_INC, signal_function_1)
        self.assertTrue(signal_function_1 in TestModel._get_callbacks_for_signal(TestModel.BEFORE_INC))
        TestModel.disconnect_from_signal(TestModel.BEFORE_INC, signal_function_1)
        self.assertFalse(signal_function_1 in TestModel._get_callbacks_for_signal(TestModel.BEFORE_INC))

    def test_pre_signal_works(self):
        TestModel.connect_to_signal(TestModel.BEFORE_INC, signal_function_1)
        model = TestModel()
        model.inc_a()
        self.assertEqual(model.b, 5)

    def test_post_signal_works(self):
        TestModel.connect_to_signal(TestModel.AFTER_INC, signal_function_2)
        model = TestModel()
        model.inc_a()
        self.assertEqual(model.a, 3)  # second inc is done by signal_function_2

    def test_both_signals_work(self):
        TestModel.connect_to_signal(TestModel.BEFORE_INC, signal_function_1)
        TestModel.connect_to_signal(TestModel.AFTER_INC, signal_function_2)
        model = TestModel()
        model.inc_a()
        self.assertEqual(model.a, 3)  # second inc is done by signal_function_2
        self.assertEqual(model.b, 5)
