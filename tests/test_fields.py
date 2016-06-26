import datetime
from decimal import Decimal

import unittest

from fixedwidthtext.fields import (
    Field, DecimalField, IntegerField, DateField, StringField)

from fixedwidthtext import exceptions


class TestField(unittest.TestCase):
    def setUp(self):
        self.field = Field(size=10)

    def test_field_should_have_verbose_name(self):
        self.assertTrue(hasattr(self.field, 'verbose_name'))

    def test_field_should_have_name(self):
        self.assertTrue(hasattr(self.field, 'name'))

    def test_field_should_have_size(self):
        self.assertTrue(hasattr(self.field, 'size'))

    def test_field_should_have_choices(self):
        self.assertTrue(hasattr(self.field, 'choices'))

    def test_field_should_have_error_messages(self):
        self.assertTrue(hasattr(self.field, 'error_messages'))

    def test_field_should_have_default(self):
        self.assertTrue(hasattr(self.field, 'default'))

    def test_field_should_have_validators(self):
        self.assertTrue(hasattr(self.field, 'validators'))

    def test_should_raise_validation_error_if_size_equals_none(self):
        with self.assertRaises(exceptions.ValidationError):
            Field(size=None)

    def _default_attr(self):
        return {
            'size': 10,
            'name': 'value'
        }

    def _object(self, value):
        class TO(object):
            def __init__(self):
                self.value = value
        return TO()

class TestStringField(TestField):
    def setUp(self):
        self.field = StringField(name='value', size=50)
        self.value = 'Nome Sobrenome'
        self.str_value = 'Nome Sobrenome                                    '
        self.object = self._object(self.value)

    def test_value_to_string_should_return_correct_string(self):
        response = self.field.value_to_string(self.object)
        self.assertEqual(response, self.str_value)
        self.assertEqual(len(response), self.field.size)

    def test_to_python_should_return_correct_string(self):
        response = self.field.to_python(self.str_value)
        self.assertEqual(response, self.value)

    def test_to_python_should_raise_validation_error_with_invalid(self):
        with self.assertRaises(exceptions.ValidationError):
            self.field.to_python(datetime.date.today())


class TestDateField(TestField):
    def setUp(self):
        self.field = DateField(**self._default_attr())
        self.value = datetime.date(2016, 6, 4)
        self.str_value = '20160604'
        self.object = self._object(self.value)

    def test_value_to_string_should_return_correct_string(self):
        response = self.field.value_to_string(self.object)
        self.assertEqual(response, self.str_value)

    def test_to_python_should_return_correct_date(self):
        response = self.field.to_python(self.str_value)
        self.assertEqual(response, self.value)

    def test_to_python_should_raise_validation_error_with_invalid(self):
        with self.assertRaises(exceptions.ValidationError):
            self.field.to_python('avc')


class TestIntegerField(TestField):
    def setUp(self):
        self.field = IntegerField(**self._default_attr())
        self.object = self._object(40)

    def test_value_to_string_should_return_correct_string(self):
        response = self.field.value_to_string(self.object)
        self.assertEqual(response, '0000000040')
        self.assertEqual(len(response), 10)

    def test_to_python_should_return_correct_integer(self):
        response = self.field.to_python('0000012345')
        self.assertEqual(response, 12345)

    def test_to_python_should_raise_validation_error_with_invalid(self):
        with self.assertRaises(exceptions.ValidationError):
            self.field.to_python('avc')


class TestDecimalField(TestField):
    def setUp(self):
        self.field = DecimalField(size=10, decimal_places=2, name='value')
        self.object = self._object(Decimal('123.45'))

    def test_value_to_string_should_return_correct_string(self):
        response = self.field.value_to_string(self.object)
        self.assertEqual(response, '0000012345')
        self.assertEqual(len(response), 10)

    def test_to_python_should_return_correct_decimal(self):
        response = self.field.to_python('0000012345')
        self.assertEqual(response, Decimal('123.45'))

    def test_to_python_should_raise_validation_error_with_invalid(self):
        with self.assertRaises(exceptions.ValidationError):
            self.field.to_python('avc')

