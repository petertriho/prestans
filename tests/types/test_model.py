import unittest

from prestans import exception
from prestans.parser import AttributeFilter
from prestans import types


class ModelUnitTest(unittest.TestCase):

    def test_required(self):
        class MyModel(types.Model):
            pass

        required_default = MyModel()
        self.assertTrue(required_default._required)

        required_true = MyModel(required=True)
        self.assertTrue(required_true._required)

        required_false = MyModel(required=False)
        self.assertFalse(required_false._required)

    def test_default(self):
        pass

    def test_description(self):
        class MyModel(types.Model):
            pass

        description_default = MyModel()
        self.assertIsNone(description_default._description)

        description_value = MyModel(description="description")
        self.assertEqual(description_value._description, "description")

    def test_attribute_count(self):
        class EmptyModel(types.Model):
            pass

        self.assertEqual(EmptyModel().attribute_count(), 0)

        class BasicTypesOnly(types.Model):
            name = types.String()
            age = types.Integer()

        self.assertEqual(BasicTypesOnly().attribute_count(), 2)

        class ModelWithArray(types.Model):
            name = types.String()
            age = types.Integer()
            tags = types.Array(element_template=types.String())

        self.assertEqual(ModelWithArray().attribute_count(), 3)

        class SubModel(types.Model):
            pass

        class ModelWithSub(types.Model):
            name = types.String()
            age = types.Integer()
            sub = SubModel()

        self.assertEqual(ModelWithSub().attribute_count(), 3)

        class ModelWithSubAndArray(types.Model):
            name = types.String()
            age = types.Integer()
            tags = types.Array(element_template=types.String())
            sub = SubModel()

        self.assertEqual(ModelWithSubAndArray().attribute_count(), 4)

    def test_blueprint(self):
        class MyModel(types.Model):
            nick_name = types.String(required=True)
            first_name = types.String(required=True)
            last_name = types.String(required=False)

        blueprint = MyModel(required=False, description="description").blueprint()
        self.assertEqual(blueprint["type"], "model")
        self.assertEqual(blueprint["constraints"]["required"], False)
        self.assertEqual(blueprint["constraints"]["description"], "description")
        self.assertEqual(blueprint["fields"]["nick_name"], MyModel.nick_name.blueprint())
        self.assertEqual(blueprint["fields"]["first_name"], MyModel.first_name.blueprint())
        self.assertEqual(blueprint["fields"]["last_name"], MyModel.last_name.blueprint())

    def test_blueprint_bad_attribute(self):
        class ModelWithBadAttribute(types.Model):
            name = "string"

        self.assertRaises(TypeError, ModelWithBadAttribute().blueprint)

    def test_setattr(self):
        class SubModel(types.Model):
            string = types.String()

        class MyModel(types.Model):
            boolean = types.Boolean()
            float = types.Float()
            age = types.Integer(maximum=120)
            name = types.String()

            sub_model = SubModel()

        sub_model = SubModel()
        sub_model.string = "string"
        self.assertEqual(sub_model.string, "string")

        my_model = MyModel()
        my_model.boolean = True
        my_model.name = "name"
        my_model.age = 21
        my_model.sub_model = sub_model
        self.assertEqual(my_model.boolean, True)
        self.assertEqual(my_model.name, "name")
        self.assertEqual(my_model.age, 21)
        self.assertEqual(my_model.sub_model, sub_model)
        self.assertEqual(my_model.sub_model.string, "string")
        self.assertRaises(KeyError, my_model.__setattr__, "missing", "missing")
        self.assertRaises(exception.ValidationError, my_model.__setattr__, "age", 121)

    def test_create_instance_attributes(self):
        class MyModel(types.Model):
            string = types.String(default="default")
            nothing = None

        my_model = MyModel()
        self.assertEqual(my_model.string, "default")
        my_model = MyModel(string="string")
        self.assertEqual(my_model.string, "string")
        self.assertEqual(my_model.nothing, None)

    def test_get_attribute_keys(self):
        class MyModel(types.Model):
            name = types.String()
            tags = types.Array(element_template=types.String())

        my_model = MyModel()
        self.assertEqual(my_model.get_attribute_keys(), ["name", "tags"])

    def test_get_attribute_filter_base(self):
        attribute_filter = types.Model().get_attribute_filter()
        self.assertEqual(attribute_filter.keys(), [])

    def test_get_attribute_filter(self):
        class SubModel(types.Model):
            colour = types.String()

        class MyModel(types.Model):
            name = types.String()
            sub = SubModel()

        my_model = MyModel()
        attribute_filter = my_model.get_attribute_filter(default_value=True)
        self.assertTrue(attribute_filter.name)
        self.assertTrue(attribute_filter.sub)
        self.assertTrue(attribute_filter.sub.colour)
        self.assertEqual(attribute_filter.keys(), ["name", "sub"])

    def test_attribute_rewrite_map(self):
        class MyModel(types.Model):
            name = types.String()
            first_name = types.String()
            last_name = types.String()

        rewrite_map = {
            "first_name": "a_c",
            "last_name": "b_c",
            "name": "c"
        }

        my_model = MyModel()
        self.assertEqual(my_model.attribute_rewrite_map(), rewrite_map)

    def test_attribute_rewrite_reverse_map(self):
        class MyModel(types.Model):
            name = types.String()
            first_name = types.String()
            last_name = types.String()

        reverse_map = {
            "a_c": "first_name",
            "b_c": "last_name",
            "c": "name"
        }

        my_model = MyModel()
        self.assertEqual(my_model.attribute_rewrite_reverse_map(), reverse_map)

    def test_contains(self):

        class SubModel(types.Model):
            pass

        # check if key can be found in model
        class MyModel(types.Model):
            name = types.String()
            birthday = types.Date()
            tags = types.Array(element_template=types.String())
            sub = SubModel()
            sub_array = types.Array(element_template=SubModel())
        my_model = MyModel()
        self.assertTrue("name" in my_model)
        self.assertTrue("birthday" in my_model)
        self.assertTrue("tags" in my_model)
        self.assertTrue("sub" in my_model)
        self.assertTrue("sub_array" in my_model)
        self.assertFalse("missing"in my_model)

        # check if keys can be found in model and base class
        class ModelWithSingleBase(MyModel):
            extra = types.String()

        single_base = ModelWithSingleBase()
        self.assertTrue("name" in single_base)
        self.assertTrue("birthday" in single_base)
        self.assertTrue("tags" in single_base)
        self.assertTrue("sub" in single_base)
        self.assertTrue("sub_array" in single_base)
        self.assertTrue("extra" in single_base)
        self.assertFalse("missing" in single_base)

        class ModelWithMultiBase(ModelWithSingleBase):
            another = types.String()

        multi_base = ModelWithMultiBase()
        self.assertTrue("name" in multi_base)
        self.assertTrue("birthday" in multi_base)
        self.assertTrue("tags" in multi_base)
        self.assertTrue("sub" in multi_base)
        self.assertTrue("sub_array" in multi_base)
        self.assertTrue("extra" in multi_base)
        self.assertTrue("another" in multi_base)
        self.assertFalse("missing" in multi_base)

    def test_generate_attribute_token_rewrite_map(self):
        class MyModel(types.Model):
            boolean = types.Boolean()
            float = types.Float()
            integer = types.Integer()
            string = types.String()

        my_model = MyModel()
        rewrite_map = my_model.generate_attribute_token_rewrite_map()
        self.assertEqual(
            rewrite_map,
            {
                "boolean": "a",
                "float": "b",
                "integer": "c",
                "string": "d"
            }
        )

    def test_generate_attribute_tokens(self):
        class MyModel(types.Model):
            boolean = types.Boolean()
            float = types.Float()
            integer = types.Integer()
            string = types.String()
        my_model = MyModel()
        tokens = my_model.generate_attribute_tokens()
        self.assertEqual(tokens, ["boolean", "float", "integer", "string"])

    def test_generate_minified_keys(self):
        self.assertEqual(types.Model.generate_minified_keys(3), ["a", "b", "c"])
        self.assertEqual(types.Model.generate_minified_keys(5), ["a", "b", "c", "d", "e"])

        self.assertEqual(types.Model.generate_minified_keys(3, "_"), ["_a", "_b", "_c"])
        self.assertEqual(types.Model.generate_minified_keys(5, "_"), ["_a", "_b", "_c", "_d", "_e"])

        self.assertEqual(types.Model.generate_minified_keys(29), [
            "a", "b", "c", "d", "e", "f", "g", "h", "i",
            "j", "k", "l", "m", "n", "o", "p", "q", "r",
            "s", "t", "u", "v", "w", "x", "y", "z",
            "aa", "ab", "ac"
        ])

        self.assertEqual(types.Model.generate_minified_keys(55), [
            "a", "b", "c", "d", "e", "f", "g", "h", "i",
            "j", "k", "l", "m", "n", "o", "p", "q", "r",
            "s", "t", "u", "v", "w", "x", "y", "z",
            "aa", "ab", "ac", "ad", "ae", "af", "ag", "ah", "ai",
            "aj", "ak", "al", "am", "an", "ao", "ap", "aq", "ar",
            "as", "at", "au", "av", "aw", "ax", "ay", "az",
            "ba", "bb", "bc"
        ])

    def test__generate_attribute_key(self):
        self.assertEqual(types.Model.generate_attribute_key(0), "a")
        self.assertEqual(types.Model.generate_attribute_key(1), "b")
        self.assertEqual(types.Model.generate_attribute_key(25), "z")
        self.assertEqual(types.Model.generate_attribute_key(26), "aa")
        self.assertEqual(types.Model.generate_attribute_key(27), "bb")
        self.assertEqual(types.Model.generate_attribute_key(51), "zz")
        self.assertEqual(types.Model.generate_attribute_key(52), "aaa")
        self.assertEqual(types.Model.generate_attribute_key(54), "ccc")
        self.assertEqual(types.Model.generate_attribute_key(77), "zzz")


class ModelAsSerializable(unittest.TestCase):

    def test_as_serializable(self):
        from datetime import date
        from datetime import datetime
        from datetime import time

        class SubModel(types.Model):
            name = types.String()

        class MyModel(types.Model):
            boolean = types.Boolean()
            float = types.Float()
            integer = types.Integer()
            string = types.String()

            date = types.Date()
            datetime = types.DateTime()
            time = types.Time()

            sub = SubModel()

        my_model = MyModel()
        my_model.boolean = True
        my_model.float = 33.3
        my_model.integer = 22
        my_model.string = "string"
        my_model.date = date(2018, 1, 18)
        my_model.datetime = datetime(2018, 1, 18, 13, 14, 15)
        my_model.time = time(12, 13, 14)
        my_model.sub.name = "name"

        serialized = my_model.as_serializable()
        self.assertTrue(isinstance(serialized, dict))
        self.assertEqual(serialized["boolean"], True)
        self.assertEqual(serialized["float"], 33.3)
        self.assertEqual(serialized["integer"], 22)
        self.assertEqual(serialized["string"], "string")
        self.assertEqual(serialized["date"], "2018-01-18")
        self.assertEqual(serialized["datetime"], "2018-01-18 13:14:15")
        self.assertEqual(serialized["time"], "12:13:14")
        self.assertEqual(serialized["sub"]["name"], "name")

    def test_as_serializable_minified(self):
        from datetime import date
        from datetime import datetime
        from datetime import time

        class SubModel(types.Model):
            name = types.String()

        class MyModel(types.Model):
            boolean = types.Boolean()
            date = types.Date()
            datetime = types.DateTime()
            float = types.Float()
            integer = types.Integer()
            string = types.String()
            sub = SubModel()
            time = types.Time()

        my_model = MyModel()
        my_model.boolean = True
        my_model.float = 33.3
        my_model.integer = 22
        my_model.string = "string"
        my_model.date = date(2018, 1, 18)
        my_model.datetime = datetime(2018, 1, 18, 13, 14, 15)
        my_model.time = time(12, 13, 14)
        my_model.sub.name = "name"

        serialized = my_model.as_serializable(minified=True)
        self.assertTrue(isinstance(serialized, dict))
        self.assertEqual(serialized["a"], True)
        self.assertEqual(serialized["b"], "2018-01-18")
        self.assertEqual(serialized["c"], "2018-01-18 13:14:15")
        self.assertEqual(serialized["d"], 33.3)
        self.assertEqual(serialized["e"], 22)
        self.assertEqual(serialized["f"], "string")
        self.assertEqual(serialized["g"]["a"], "name")
        self.assertEqual(serialized["h"], "12:13:14")

    def test_as_serializable_filtered_default_true(self):
        from datetime import date
        from datetime import datetime
        from datetime import time
        from prestans.parser import AttributeFilter

        class SubModel(types.Model):
            name = types.String()

        class MyModel(types.Model):
            boolean = types.Boolean()
            date = types.Date()
            datetime = types.DateTime()
            float = types.Float()
            integer = types.Integer()
            string = types.String()
            sub = SubModel()
            time = types.Time()

        my_model = MyModel()
        my_model.boolean = True
        my_model.float = 33.3
        my_model.integer = 22
        my_model.string = "string"
        my_model.date = date(2018, 1, 18)
        my_model.datetime = datetime(2018, 1, 18, 13, 14, 15)
        my_model.time = time(12, 13, 14)
        my_model.sub.name = "name"

        attribute_filter = AttributeFilter.from_model(MyModel(), True)
        attribute_filter.float = False
        attribute_filter.string = False

        serialized = my_model.as_serializable(attribute_filter=attribute_filter)
        self.assertTrue(isinstance(serialized, dict))
        self.assertEqual(serialized["boolean"], True)
        self.assertTrue("float" not in serialized)
        self.assertEqual(serialized["integer"], 22)
        self.assertTrue("string" not in serialized)
        self.assertEqual(serialized["date"], "2018-01-18")
        self.assertEqual(serialized["datetime"], "2018-01-18 13:14:15")
        self.assertEqual(serialized["time"], "12:13:14")
        self.assertEqual(serialized["sub"]["name"], "name")

    def test_as_serializable_filtered_default_false(self):
        from datetime import date
        from datetime import datetime
        from datetime import time
        from prestans.parser import AttributeFilter

        class SubModel(types.Model):
            name = types.String()

        class MyModel(types.Model):
            boolean = types.Boolean()
            date = types.Date()
            datetime = types.DateTime()
            float = types.Float()
            integer = types.Integer()
            string = types.String()
            sub = SubModel()
            time = types.Time()

        my_model = MyModel()
        my_model.boolean = True
        my_model.float = 33.3
        my_model.integer = 22
        my_model.string = "string"
        my_model.date = date(2018, 1, 18)
        my_model.datetime = datetime(2018, 1, 18, 13, 14, 15)
        my_model.time = time(12, 13, 14)
        my_model.sub.name = "name"

        attribute_filter = AttributeFilter.from_model(MyModel(), False)
        attribute_filter.float = True
        attribute_filter.string = True

        serialized = my_model.as_serializable(attribute_filter=attribute_filter)
        self.assertEqual(serialized, {"float": 33.3, "string": "string"})

        attribute_filter = AttributeFilter.from_model(MyModel(), False)
        attribute_filter.sub.name = True

        serialized = my_model.as_serializable(attribute_filter=attribute_filter)
        self.assertEqual(serialized, {"sub": {"name": "name"}})

    def test_as_serializable_filtered_only_child_of_type_model(self):
        from prestans.parser import AttributeFilter

        class SubModel(types.Model):
            name = types.String()

        class ParentModel(types.Model):
            sub = SubModel()

        attribute_filter = AttributeFilter.from_model(ParentModel(), False)
        attribute_filter.sub.name = True

        parent_model = ParentModel()
        parent_model.sub.name = "james"

        serialized = parent_model.as_serializable(attribute_filter=attribute_filter)
        self.assertEqual(serialized, {"sub": {"name": "james"}})

    def test_none_attributes_skips_further_checks(self):
        class Person(types.Model):
            first_name = types.String(required=True)
            last_name = types.String(required=False)

        person = Person(first_name="Carol")
        serialized = person.as_serializable()
        self.assertEqual(serialized["first_name"], "Carol")
        self.assertEqual(serialized["last_name"], None)


class ModelValidate(unittest.TestCase):
    def test_required_rejects_none(self):

        class MyModel(types.Model):
            pass

        self.assertRaises(exception.RequiredAttributeError, MyModel(required=True).validate, None)

    def test_required_rejects_non_dict_type(self):

        class MyModel(types.Model):
            pass

        self.assertRaises(exception.RequiredAttributeError, MyModel(required=True).validate, False)
        self.assertRaises(exception.RequiredAttributeError, MyModel(required=True).validate, 3)
        self.assertRaises(exception.RequiredAttributeError, MyModel(required=True).validate, 3.33)
        self.assertRaises(exception.RequiredAttributeError, MyModel(required=True).validate, "string")

    def test_not_required_accepts_none(self):
        class MyModel(types.Model):
            pass

        self.assertEqual(MyModel(required=False).validate(None), None)

    def test_sets_none_for_invisible_attributes(self):
        class MyModel(types.Model):
            visible = types.String(default="visible")
            invisible = types.String(default="invisible")

        my_model = MyModel()
        import logging
        logging.error(my_model.visible)
        logging.error(my_model.invisible)

        self.assertEqual(my_model.visible, "visible")
        self.assertEqual(my_model.invisible, "invisible")

        attribute_filter = AttributeFilter.from_model(MyModel(), default_value=False)
        attribute_filter.visible = True

        validated = my_model.validate({}, attribute_filter)
        self.assertEqual(validated.visible, "visible")
        self.assertEqual(validated.invisible, None)

        attribute_filter.visible = False
        attribute_filter.invisible = True

        validated = my_model.validate({}, attribute_filter)
        self.assertIsNone(validated.visible)
        self.assertEqual(validated.invisible, "invisible")

    @unittest.skip(reason="these are ignored instead of raising TypeError since prestans 2.5.0")
    def test_rejects_bad_attribute_type(self):

        class MyModel(types.Model):
            bad_attribute_type = "string"

        self.assertRaises(TypeError, MyModel().validate, {})

    def test_child_data_collection(self):
        class ChildModel(types.Model):
            age = types.Integer()

        class ParentModel(types.Model):
            name = types.String()
            child = ChildModel()

        parent_model = ParentModel()
        parent_model.name = "Nathan"
        parent_model.child.age = 30

        validated = ParentModel().validate(parent_model.as_serializable())
        self.assertEqual(validated.name, "Nathan")
        self.assertEqual(validated.child.age, 30)

    def test_child_model_filtered(self):
        class ChildModel(types.Model):
            child_name = types.String()
            child_age = types.Integer()

        class ParentModel(types.Model):
            parent_name = types.String()
            parent_percent = types.Float()
            child = ChildModel()

        parent_model = ParentModel()
        parent_model.parent_name = "Nathan"
        parent_model.parent_percent = 33.3
        parent_model.child.child_name = "Steve"
        parent_model.child.child_age = 30

        parent_filter = AttributeFilter.from_model(ParentModel(default=False))
        parent_filter.parent_name = True
        parent_filter.parent_percent = True
        parent_filter.child.child_name = True
        parent_filter.child.child_age = True

        validated = ParentModel().validate(parent_model.as_serializable(attribute_filter=parent_filter))
        self.assertEqual(validated.parent_name, "Nathan")
        self.assertEqual(validated.parent_percent, 33.3)
        self.assertEqual(validated.child.child_name, "Steve")
        self.assertEqual(validated.child.child_age, 30)

        parent_filter.parent_name = False
        parent_filter.child.child_name = False

        validated = ParentModel().validate(
            parent_model.as_serializable(attribute_filter=parent_filter),
            attribute_filter=parent_filter
        )
        self.assertEqual(validated.parent_name, None)
        self.assertEqual(validated.parent_percent, 33.3)
        self.assertEqual(validated.child.child_name, None)
        self.assertEqual(validated.child.child_age, 30)

    def test_child_array_filtered(self):
        class ChildModel(types.Model):
            child_name = types.String()
            child_age = types.Integer()

        class ParentModel(types.Model):
            parent_name = types.String()
            parent_percent = types.Float()
            children = types.Array(element_template=ChildModel())

        parent_model = ParentModel()
        parent_model.parent_name = "Nathan"
        parent_model.parent_percent = 33.3

        child_model = ChildModel()
        child_model.child_name = "Steve"
        child_model.child_age = 30
        parent_model.children.append(child_model)

        parent_filter = AttributeFilter.from_model(ParentModel(default=False))
        parent_filter.parent_name = True
        parent_filter.parent_percent = True
        parent_filter.children.child_name = True
        parent_filter.children.child_age = True

        validated = ParentModel().validate(parent_model.as_serializable(attribute_filter=parent_filter))
        self.assertEqual(validated.parent_name, "Nathan")
        self.assertEqual(validated.parent_percent, 33.3)
        self.assertEqual(validated.children[0].child_name, "Steve")
        self.assertEqual(validated.children[0].child_age, 30)

        parent_filter.parent_name = False
        parent_filter.children.child_name = False

        validated = ParentModel().validate(
            parent_model.as_serializable(attribute_filter=parent_filter),
            attribute_filter=parent_filter
        )
        self.assertEqual(validated.parent_name, None)
        self.assertEqual(validated.parent_percent, 33.3)
        self.assertEqual(validated.children[0].child_name, None)
        self.assertEqual(validated.children[0].child_age, 30)

    def test_multi_levels_of_array_filtered(self):
        class ChildB(types.Model):
            child_b_name = types.String()
            child_b_age = types.Integer()

        class ChildA(types.Model):
            child_a_name = types.String()
            child_a_age = types.Integer()
            children = types.Array(element_template=ChildB())

        class ParentModel(types.Model):
            parent_name = types.String()
            parent_percent = types.Float()
            children = types.Array(element_template=ChildA())

        parent_model = ParentModel()
        parent_model.parent_name = "Nathan"
        parent_model.parent_percent = 33.3

        child_model_a = ChildA()
        child_model_a.child_a_name = "Steve"
        child_model_a.child_a_age = 30

        child_model_b = ChildB()
        child_model_b.child_b_name = "Betty"
        child_model_b.child_b_age = 54

        child_model_a.children.append(child_model_b)
        parent_model.children.append(child_model_a)

        parent_filter = AttributeFilter.from_model(ParentModel(default=False))
        parent_filter.parent_name = True
        parent_filter.parent_percent = True
        parent_filter.children.child_a_name = True
        parent_filter.children.child_a_age = True
        parent_filter.children.children.child_b_name = True
        parent_filter.children.children.child_b_age = True

        validated = ParentModel().validate(parent_model.as_serializable(attribute_filter=parent_filter))
        self.assertEqual(validated.parent_name, "Nathan")
        self.assertEqual(validated.parent_percent, 33.3)
        self.assertEqual(validated.children[0].child_a_name, "Steve")
        self.assertEqual(validated.children[0].child_a_age, 30)
        self.assertEqual(validated.children[0].children[0].child_b_name, "Betty")
        self.assertEqual(validated.children[0].children[0].child_b_age, 54)

        parent_filter.parent_name = False
        parent_filter.children.child_a_name = False
        parent_filter.children.children.child_b_name = False

        validated = ParentModel().validate(
            parent_model.as_serializable(attribute_filter=parent_filter),
            attribute_filter=parent_filter
        )
        self.assertEqual(validated.parent_name, None)
        self.assertEqual(validated.parent_percent, 33.3)
        self.assertEqual(validated.children[0].child_a_name, None)
        self.assertEqual(validated.children[0].child_a_age, 30)
        self.assertEqual(validated.children[0].children[0].child_b_name, None)
        self.assertEqual(validated.children[0].children[0].child_b_age, 54)

    def test_minified_true(self):
        class Person(types.Model):
            first_name = types.String()
            last_name = types.String()

        person = Person(first_name="john", last_name="smith")
        person_validated = person.validate(person.as_serializable(minified=True), minified=True)
        self.assertEqual(person_validated.as_serializable(), {"first_name": "john", "last_name": "smith"})
        self.assertEqual(person_validated.as_serializable(minified=True), {"a_c": "john", "b_c": "smith"})

    def test_child_failing_to_validate_raises_validation_error(self):
        class Person(types.Model):
            first_name = types.String(required=True)
            last_name = types.String(required=True)

        person = Person(first_name="john")
        self.assertRaises(exception.ValidationError, Person().validate, person.as_serializable())
