# -*- coding: utf-8 -*-
import copy


mongodb_database = None


class ModelMetaClass(type):
    def __new__(cls, name, bases, _dict):
        _dict['db'] = None

        # fetching fields
        _dict['_fields'] = [k for k, v in _dict.iteritems() if type(v) == Field]

        if not object in bases:
            for base in bases:
                _dict['_fields'] += getattr(base, '_fields', [])

        return type.__new__(cls, name, bases, _dict)


class BaseFieldClass(object):
    def __init__(self, default=None):
        self.default = copy.deepcopy(default)
        self.value = copy.deepcopy(default)

    def get(self):
        return self.value

    def set(self, value):
        self.value = copy.deepcopy(value)

    def default(self):
        return copy.deepcopy(self.default)


class Field(object):
    """
    This is basically a factory for BaseFieldClass.
    Use it when creating your models.
    """
    def __init__(self, default=None):
        self.default = default

    def construct(self):
        return BaseFieldClass(default=self.default)


class Model(object):
    __metaclass__ = ModelMetaClass

    _objects = None  # mongodb objects
    _collection = ''  # must be overridden to set proper collection name

    _initialized = False

    _id = Field()  # all models will have it

    def __init__(self):

        super(Model, self).__init__()
        self._objects = getattr(mongodb_database, self._collection)

        # constructing fields from Field factory
        for field in self._fields:
            if hasattr(self, field):
                setattr(self, field, getattr(self, field).construct())
        self._initialized = True

    def __getattribute__(self, name):
        if name in ('_fields', '_initialized'):
            return object.__getattribute__(self, name)

        if self._initialized and name in self._fields:
            return object.__getattribute__(self, name).get()
        else:
            # Default behaviour
            return object.__getattribute__(self, name)

    def __setattr__(self, key, value):
        if self._initialized and key in self._fields:
            object.__getattribute__(self, key).set(value)
        else:
            # Default behaviour
            object.__setattr__(self, key, value)

    def find(self, where):
        """
        Fill model instance with values from mongodb.
        """
        found = self._objects.find_one(where)

        if found:
            for k, v in found.iteritems():
                if k in self._fields:
                    setattr(self, k, v)
        return bool(found)

    def delete(self, where=None):
        if where:
            self._objects.remove(where)
        elif self._id:
            self._objects.remove({'_id': self._id})
        else:
            raise Exception('You tried to delete everything!')

    def save(self):
        """
        Saving model into mongodb.
        """
        _data = {field: getattr(self, field, None) for field in self._fields}
        del _data['_id']

        if self._id:
            # update
            self._objects.update({'_id': self._id}, {'$set': _data}, safe=True)
        else:
            # insert
            self._id = self._objects.insert(_data)
