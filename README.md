===========
Miongo
===========

Yet another MongoDB ORM for Python.
Signals included!

Still in development, feedback is highly appreciated.


Usage Examples
==============

Installation

    pip install miongo

Models
-------------

Here's a simple example of model usage

    #!/usr/bin/env python
    import pymongo
    from miongo import models

    # this is always required
    # miongo do not implement mongodb connection, you should do that
    models.mongodb_database = pymongo.MongoClient().test_database


    class TestModel(models.Model):
        _collection = 'testmodel'

        uid = models.Field()
        name = models.Field()
        enabled = models.Field(default=True)

    # creating and saving
    model = TestModel()
    model.uid = 1
    model.name = 'Antony'
    model.save()

    # finding in db
    model = TestModel()
    model.find({'uid': 1})
    print model.uid  # 1
    print model.name  # Antony
    print model.enabled  # True

Signals
-------
Signals can be used independently with your models too! Just use `signals.SignalEmitterMixin`, specify `AVAILABLE_SIGNALS` and call `self.emit_signal(signal_type)` to fire a signal when needed.

Here's an example of implementing before and after save signals

    #!/usr/bin/env python
    import pymongo
    from miongo import signals, models

    models.mongodb_database = pymongo.MongoClient().test_database

    # signals.SignalEmitterMixin is important here
    # it also can be used with other model classes
    class TestModel(models.Model, signals.SignalEmitterMixin):
        _collection = 'testmodel'

        BEFORE_SAVE = 0
        AFTER_SAVE = 1
        AVAILABLE_SIGNALS = [BEFORE_SAVE, AFTER_SAVE]

        name = models.Field()

        def save(self):
            self.emit_signal(self.BEFORE_SAVE)
            print 'Saving now!'
            super(TestModel, self).save()
            self.emit_signal(self.AFTER_SAVE)

    # let's define function that will be used by signal
    # you may use instance to modify object
    def signal_function(signal_type, instance):
        if signal_type == TestModel.BEFORE_SAVE:
            print 'Before save'
        elif signal_type == TestModel.AFTER_SAVE:
            print 'After save'

    model = TestModel()

    TestModel.connect_to_signal(TestModel.BEFORE_SAVE, signal_function)
    TestModel.connect_to_signal(TestModel.AFTER_SAVE, signal_function)

    model.save()

    # output is:
    #
    # Before save
    # Saving now!
    # After save

(Note signals can be connected to the instance too)

Credits
=======

Author:
Anton Kasyanov (antony.kasyanov@gmail.com)

Special thanks to:
Ruslan Didyk, Igor Emelyanov
