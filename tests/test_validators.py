"""Tests for custom validators in the geometry_constructor.validators module"""
from geometry_constructor.validators import NameValidator, TransformParentValidator
from geometry_constructor.instrument_model import InstrumentModel
from geometry_constructor.data_model import Component
from PySide2.QtGui import QValidator


def assess_component_tree(count: int, parent_mappings: dict, results: dict):
    """
    Test the validity of a transform parent network of components

    Builds an InstrumentModel with components connected according to parent_mappings, then for each provided result,
    checks a components validity if it were to be set to its current parent.
    :param count: the number of components to create
    :param parent_mappings: a dictionary of int -> int representing child and parent index numbers
    :param results: a dictionary of int -> boolean representing the index of components to check validity for, and
    their expected validity
    """
    components = [Component(name=str(i)) for i in range(count)]
    for child, parent in parent_mappings.items():
        components[child].transform_parent = components[parent]

    model = InstrumentModel()
    model.components = components

    validator = TransformParentValidator()
    validator.instrument_model = model

    for index, expected_result in results.items():
        validator.model_index = index
        parent_name = components[index].transform_parent.name
        assert (validator.validate(parent_name, 0) == QValidator.Acceptable) == expected_result


def test_parent_validator_self_loop_terminated_tree():
    """A parent tree where the root item points to itself is valid"""
    parent_mappings = {
        0: 0,
        1: 0,
        2: 1,
        3: 1,
        4: 0,
    }
    results = {
        0: True,
        1: True,
        2: True,
        3: True,
        4: True,
    }
    assess_component_tree(5, parent_mappings, results)


def test_parent_validator_none_terminated_tree():
    """A parent tree where the root item has no parent is valid"""
    parent_mappings = {
        1: 0,
        2: 1,
        3: 1,
        4: 0,
    }
    results = {
        1: True,
        2: True,
        3: True,
        4: True,
    }
    assess_component_tree(5, parent_mappings, results)


def test_parent_validator_2_item_loop():
    """A loop between two items is invalid, as would be any item with its parent in that loop"""
    parent_mappings = {
        0: 1,
        1: 0,
        2: 1,
    }
    results = {
        0: False,
        1: False,
        2: False,
    }
    assess_component_tree(3, parent_mappings, results)


def test_parent_validator_3_item_loop():
    """A loop between three items is invalid, and items with parents in that loop should be too"""
    parent_mappings = {
        0: 1,
        1: 2,
        2: 0,
        3: 2,
    }
    results = {
        0: False,
        1: False,
        2: False,
        3: False,
    }
    assess_component_tree(4, parent_mappings, results)


def test_parent_validator_chain_beside_loop():
    """Even if there's a loop, items disconnected from it would still be valid"""
    parent_mappings = {
        0: 1,
        1: 0,
        2: 2,
        3: 2,
    }
    results = {
        0: False,
        1: False,
        2: True,
        3: True,
    }
    assess_component_tree(4, parent_mappings, results)


def assess_component_names(names: list, index, new_name, expected_validity):
    """
    Tests the validity of a given name at a given index in an InstrumentModel with an existing list of named components

    :param names: The names to give to components in the model before validating a change
    :param index: The index to change/insert the new name at in the model
    :param new_name: The name to check the validity of a change/insert into the model
    :param expected_validity: Whether the name change/insert is expected to be valid
    """
    model = InstrumentModel()
    model.components = [Component(name=name) for name in names]

    validator = NameValidator()
    validator.instrument_model = model
    validator.model_index = index

    assert (validator.validate(new_name, 0) == QValidator.Acceptable) == expected_validity


def test_name_validator_new_unique_name():
    """A name that's not already in the model, being added at a new index should be valid"""
    assess_component_names(['foo', 'bar', 'baz'], 3, 'asdf', True)


def test_name_validator_new_existing_name():
    """A name that is already in the model is not valid at a new index"""
    assess_component_names(['foo', 'bar', 'baz'], 3, 'foo', False)


def test_name_validator_set_to_new_name():
    """A name that's not in the model should be valid at an existing index"""
    assess_component_names(['foo', 'bar', 'baz'], 1, 'asdf', True)


def test_name_validator_set_to_current_name():
    """A name should be valid at an index where it's already present"""
    assess_component_names(['foo', 'bar', 'baz'], 1, 'bar', True)


def test_name_validator_set_to_duplicate_name():
    """A name that's already at an index should not be valid at another index"""
    assess_component_names(['foo', 'bar', 'baz'], 1, 'foo', False)