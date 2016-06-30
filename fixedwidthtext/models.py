# coding: utf-8
from collections import OrderedDict
import six

from fixedwidthtext import exceptions
from fixedwidthtext.fields import Field

RESERVED_FIELD_NAMES = ['line']


class Options(object):
    def __init__(self, attrs):
        self.fields = []
        self.total_size = 0
        self.verbose_name = None
        self._prepare(attrs)

    def _prepare(self, attrs):
        self._add_fields_names(attrs)
        self._populate_fields(attrs)
        self._compute_total_size()

    def _compute_total_size(self):
        total = 0
        for field in self.fields.values():
            total += field.size
        self.total_size = total

    def _add_fields_names(self, attrs):
        for name, field in attrs.items():
            if isinstance(field, Field):
                if name in RESERVED_FIELD_NAMES:
                    raise exceptions.ValidationError(
                        '%s in reserved names, please chose another name.' %
                        name)
                field.name = name

    def _populate_fields(self, attrs):
        attrs = filter(
            lambda x: hasattr(x[1], 'creation_counter'), attrs.items())
        self.fields = OrderedDict(
            sorted(attrs, key=lambda x: x[1].creation_counter))


class ModelBase(type):
    """
    Metaclass for all models.
    """
    def __init__(self, *args, **kwargs):
        super(ModelBase, self).__init__(*args, **kwargs)

    def __new__(cls, name, bases, attrs):
        super_new = super(ModelBase, cls).__new__

        if name == 'NewBase' and attrs == {}:
            return super_new(cls, name, bases, attrs)

        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})

        new_class.add_to_class('_meta', Options(attrs))

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)
        return new_class

    def add_to_class(cls, name, value):
        setattr(cls, name, value)


class LineManager(six.with_metaclass(ModelBase)):
    def __init__(self, **kwargs):
        if 'string' in kwargs:
            self._parse_and_populate(kwargs['string'])
        else:
            self._populate_fields(kwargs)
        self.clean_fields()

    def _populate_fields(self, dictionary):
        for name, field in self._meta.fields.items():
            setattr(self, name, dictionary.get(name, None))

    def _parse_and_populate(self, string):
        self._validate_string(string)
        index = 0
        dictionary = {}
        for name, field in self._meta.fields.items():
            ending = index + field.size
            value = string[index:ending]
            dictionary[name] = value
            index = ending
        self._populate_fields(dictionary)

    def _validate_string(self, string):
        string_length = len(string)
        if string_length != self._meta.total_size:
            msg = 'String with wrong size, needed: %s, passed: %s' % (
                self._meta.total_size,
                string_length)
            raise exceptions.ValidationError(msg)

    def clean_fields(self):
        errors = {}
        for field in self._meta.fields.values():
            raw_value = getattr(self, field.name)
            try:
                setattr(self, field.name, field.clean(raw_value, self))
            except Exception as e:
                errors[field.name] = str(e)
        if errors:
            raise exceptions.ValidationError(repr(errors))

    def to_string(self):
        string = ''
        for field in self._meta.fields.values():
            string += field.value_to_string(self)
        return string

    def get_dicts(self):
        dicts = []
        for field in self._meta.fields.values():
            dicts.append(field.to_dict(self))
        return dicts
