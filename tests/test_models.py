import datetime 
from decimal import Decimal

from fixedwidthtext.models import LineManager, Options
from fixedwidthtext import fields

import unittest

def default_date():
    return datetime.date(2016, 12, 1)

def default_time():
    return datetime.time(8,9)

class ExampleLineManager(LineManager):
    first_name = fields.StringField(size=10)
    last_name = fields.StringField(size=10)
    age = fields.IntegerField(size=3)
    date_joined = fields.DateField(size=8, default=default_date)
    time_joined = fields.TimeField(size=4, default=default_time)
    bank_balance = fields.DecimalField(size=8, decimal_places=2)


class TestLineManager(unittest.TestCase):
    def setUp(self):
        self.parser = ExampleLineManager(
            first_name='Joao',
            last_name='Pereira',
            age=24,
            bank_balance=Decimal(1000))

    def test_should_have_attr_media_as_options_object(self):
        self.assertTrue(hasattr(self.parser, '_meta'))
        self.assertTrue(isinstance(self.parser._meta, Options))

    def test_should_have_attr_total_size_with_correct_size(self):
        self.assertTrue(hasattr(self.parser._meta, 'total_size'))
        self.assertEqual(self.parser._meta.total_size, 43)

    def test_should_create_fields_in_meta_with_right_order(self):
        self.assertTrue(hasattr(self.parser._meta, 'fields'))
        self.assertEqual(
            self.parser._meta.fields.keys(),
            ['first_name', 'last_name', 'age',
             'date_joined', 'time_joined', 'bank_balance'])

    def test_init_should_validate_and_set_atributes(self):
        self.assertEqual(self.parser.first_name, 'Joao')
        self.assertEqual(self.parser.last_name, 'Pereira')
        self.assertEqual(self.parser.age, 24)

    def test_init_with_string_should_set_atributes(self):
        string = 'Pedro     Almeida   01420161201121500054312'
        parser = ExampleLineManager(string=string)
        self.assertEqual(parser.first_name, 'Pedro')
        self.assertEqual(parser.last_name, 'Almeida')
        self.assertEqual(parser.age, 14)
        self.assertEqual(parser.bank_balance, Decimal('543.12'))
        self.assertEqual(parser.date_joined, datetime.date(2016, 12, 1))
        self.assertEqual(parser.time_joined, datetime.time(12, 15))

    def test_get_dicts_should_return_array_of_dictionarys(self):
        expected = [
            {'name': 'first_name', 'value': 'Joao', 'verbose_name': 'first name'},
            {'name': 'last_name', 'value': 'Pereira', 'verbose_name': 'last name'},
            {'name': 'age', 'value': 24, 'verbose_name': 'age'},
            {'name': 'date_joined',
             'value': datetime.date(2016, 12, 1),
             'verbose_name': 'date joined'},
            {'name': 'time_joined',
             'value': datetime.time(8,9),
             'verbose_name': 'time joined'},
            {'name': 'bank_balance',
             'value': Decimal('1000'),
             'verbose_name': 'bank balance'}]

        self.assertEqual(self.parser.get_dicts(), expected)


class TestParserWrite(unittest.TestCase):
    def setUp(self):
        self.parser = ExampleLineManager(
            first_name='Joao',
            last_name='Pereira',
            bank_balance=Decimal(1000),
            age=24)

    def test_to_string_should_return_correct_string(self):
        response = self.parser.to_string()
        expected = 'Joao      Pereira   02420161201080900100000'
        self.assertEqual(response, expected)

