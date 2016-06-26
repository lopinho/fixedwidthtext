from fixedwidthtext.models import LineManager, Options
from fixedwidthtext import fields

import unittest

class ExampleLineManager(LineManager):
    first_name = fields.StringField(size=10)
    last_name = fields.StringField(size=10)
    age = fields.IntegerField(size=3)



class TestLineManager(unittest.TestCase):
    def setUp(self):
        self.parser = ExampleLineManager(
            first_name='Joao',
            last_name='Pereira',
            age=24)

    def test_should_have_attr_media_as_options_object(self):
        self.assertTrue(hasattr(self.parser, '_meta'))
        self.assertTrue(isinstance(self.parser._meta, Options))

    def test_should_have_attr_total_size_with_correct_size(self):
        self.assertTrue(hasattr(self.parser._meta, 'total_size'))
        self.assertEqual(self.parser._meta.total_size, 23)

    def test_should_create_fields_in_meta_with_right_order(self):
        self.assertTrue(hasattr(self.parser._meta, 'fields'))
        self.assertEqual(
            self.parser._meta.fields.keys(),
            ['first_name', 'last_name', 'age'])

    def test_init_should_validate_and_set_atributes(self):
        self.assertEqual(self.parser.first_name, 'Joao')
        self.assertEqual(self.parser.last_name, 'Pereira')
        self.assertEqual(self.parser.age, 24)

    def test_init_with_string_should_set_atributes(self):
        string = 'Pedro     Almeida   014'
        parser = ExampleLineManager(string=string)
        self.assertEqual(parser.first_name, 'Pedro')
        self.assertEqual(parser.last_name, 'Almeida')
        self.assertEqual(parser.age, 14)

    def test_get_dicts_should_return_array_of_dictionarys(self):
        expected = [
            {'name': 'first_name', 'value': 'Joao', 'verbose_name': 'first name'},
            {'name': 'last_name', 'value': 'Pereira', 'verbose_name': 'last name'},
            {'name': 'age', 'value': 24, 'verbose_name': 'age'}
        ]
        self.assertEqual(self.parser.get_dicts(), expected)


class TestParserWrite(unittest.TestCase):
    def setUp(self):
        self.parser = ExampleLineManager(
            first_name='Joao',
            last_name='Pereira',
            age=24)

    def test_to_string_should_return_correct_string(self):
        response = self.parser.to_string()
        expected = 'Joao      Pereira   024'
        self.assertEqual(response, expected)

