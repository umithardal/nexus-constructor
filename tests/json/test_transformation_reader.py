import json

import pytest
from PySide2.QtGui import QVector3D
from mock import Mock

from nexus_constructor.json.transformation_reader import (
    TransformationReader,
    _contains_transformations,
    TRANSFORMATION_MAP,
    _create_transformation_dataset,
)
from nexus_constructor.model.component import Component


@pytest.fixture(scope="function")
def transformation_json():
    json_string = """
    {
      "type":"group",
      "name":"transformations",
      "children":[
        {
          "type":"dataset",
          "name":"location",
          "dataset":{
            "type":"double"
          },
          "values":0.0,
          "attributes":[
            {
              "name":"units",
              "values":"m"
            },
            {
              "name":"transformation_type",
              "values":"translation"
            },
            {
              "name":"vector",
              "values":[
                0.0,
                0.0,
                0.0
              ],
              "type":"double"
            },
            {
              "name":"depends_on",
              "values":"."
            },
            {
              "name":"NX_class",
              "values":"NXtransformation"
            }
          ]
        }
      ],
      "attributes":[
        {
          "name":"NX_class",
          "values":"NXtransformations"
        }
      ]
    }
    """
    return json.loads(json_string)


@pytest.fixture(scope="function")
def attributes_list(transformation_json):
    return transformation_json["children"][0]["attributes"]


@pytest.fixture(scope="function")
def transformation_reader(transformation_json):
    parent_component = Mock(spec=Component)
    parent_component.name = "ParentComponentName"
    parent_component.transforms_list = []
    entry = [transformation_json]
    return TransformationReader(parent_component, entry)


@pytest.mark.parametrize("class_value", ["NXtransformation", "NXtransformations"])
def test_GIVEN_transformation_in_attributes_WHEN_checking_for_transformation_THEN_contains_transformations_returns_true(
    class_value, transformation_json
):
    transformation_json["attributes"][0]["values"] = class_value
    assert _contains_transformations(transformation_json)


def test_GIVEN_no_transformation_class_in_attributes_WHEN_checking_for_transformations_THEN_contains_transformations_returns_false(
    transformation_json,
):
    del transformation_json["attributes"][0]["name"]
    del transformation_json["attributes"][0]["values"]

    assert not _contains_transformations(transformation_json)


def test_GIVEN_no_attributes_field_in_dict_WHEN_checking_for_transformations_THEN_contains_transformations_returns_false(
    transformation_json,
):
    del transformation_json["attributes"]
    assert not _contains_transformations(transformation_json)


def test_GIVEN_attribute_not_found_WHEN_looking_for_transformation_attribute_THEN_get_transformation_attribute_returns_failure_value(
    transformation_json, transformation_reader
):
    n_warnings = len(transformation_reader.warnings)

    failure_value = 20
    attribute_name = "DoesNotExist"
    attribute_value = transformation_reader._get_transformation_attribute(
        attribute_name, transformation_json["children"][0], failure_value=failure_value
    )

    # Check that the failure value was returned
    assert attribute_value == failure_value
    # Check that the number of warnings has increased
    assert len(transformation_reader.warnings) == n_warnings + 1
    # Check that the latest warning mentions the name of the attribute that could not be found
    assert attribute_name in transformation_reader.warnings[-1]


def test_GIVEN_attribute_is_found_WHEN_looking_for_transformation_attribute_THEN_get_transformation_attribute_returns_attribute_value(
    transformation_json, transformation_reader
):
    n_warnings = len(transformation_reader.warnings)

    # Set the values attribute
    transformation_json["children"][0]["values"] = json_value = 300

    attribute_value = transformation_reader._get_transformation_attribute(
        "values", transformation_json["children"][0], failure_value=50
    )

    # Check that the json value was returned
    assert attribute_value == json_value
    # Check that the number of warnings has remained the same
    assert len(transformation_reader.warnings) == n_warnings


def test_GIVEN_attribute_is_in_list_WHEN_looking_for_transformation_attribute_THEN_get_attribute_in_list_returns_true(
    transformation_reader, attributes_list
):
    n_warnings = len(transformation_reader.warnings)

    # Set the units value
    attributes_list[0]["values"] = json_value = "cm"

    attribute_value = transformation_reader._find_attribute_in_list(
        "units", "TransformationName", attributes_list, failure_value="yards"
    )

    # Check that the json value was returned
    assert attribute_value == json_value
    # Check that the number of warnings has remained the same
    assert len(transformation_reader.warnings) == n_warnings


def test_GIVEN_attribute_name_not_in_list_WHEN_looking_for_transformation_attribute_THEN_get_attribute_in_list_returns_false(
    transformation_reader, attributes_list
):
    n_warnings = len(transformation_reader.warnings)
    failure_value = "yards"

    # Remove the name field from the nested units dictionary
    del attributes_list[0]["name"]

    attribute_value = transformation_reader._find_attribute_in_list(
        "units", "TransformationName", attributes_list, failure_value
    )

    # Check that the failure value was returned
    assert attribute_value == failure_value
    # Check that the number of warnings has increased
    assert len(transformation_reader.warnings) == n_warnings + 1
    # Check that the latest warning mentions the name of the attribute that could not be found
    assert "units" in transformation_reader.warnings[-1]


def test_GIVEN_attribute_value_not_in_list_WHEN_looking_for_transformation_attribute_THEN_get_attribute_in_list_returns_false(
    transformation_reader, attributes_list
):
    n_warnings = len(transformation_reader.warnings)
    failure_value = "yards"

    # Remove the values field from the nested units dictionary
    del attributes_list[0]["values"]

    attribute_value = transformation_reader._find_attribute_in_list(
        "units", "TransformationName", attributes_list, failure_value
    )

    # Check that the failure value was returned
    assert attribute_value == failure_value
    # Check that the number of warnings has increased
    assert len(transformation_reader.warnings) == n_warnings + 1
    # Check that the latest warning mentions the name of the attribute that could not be found
    assert "units" in transformation_reader.warnings[-1]


def test_GIVEN_no_values_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    del transformation_json["children"][0]["values"]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_dataset_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    del transformation_json["children"][0]["dataset"]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_datatype_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    transformation_json["children"][0]["dataset"]["a"] = "b"
    del transformation_json["children"][0]["dataset"]["type"]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_attributes_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    del transformation_json["children"][0]["attributes"]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_transformation_type_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    # Delete the transformation type nested dictionary
    del transformation_json["children"][0]["attributes"][1]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_no_units_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    # Delete the units nested dictionary
    del transformation_json["children"][0]["attributes"][0]
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_all_information_present_WHEN_attempting_to_create_translation_THEN_create_transform_is_called(
    transformation_reader, transformation_json
):
    transformation_json["children"][0]["name"] = name = "TranslationName"
    transformation_json["children"][0]["attributes"][1][
        "values"
    ] = transformation_type = "translation"
    transformation_json["children"][0]["values"] = angle_or_magnitude = 300.0
    transformation_json["children"][0]["attributes"][0]["values"] = units = "mm"
    transformation_json["children"][0]["attributes"][2]["values"] = vector = [
        1.0,
        2.0,
        3.0,
    ]
    depends_on = None

    values = _create_transformation_dataset(angle_or_magnitude, "double", name)

    transformation_reader._create_transformations(transformation_json["children"])
    transformation_reader.parent_component._create_and_add_transform.assert_called_once_with(
        name,
        TRANSFORMATION_MAP[transformation_type],
        angle_or_magnitude,
        units,
        QVector3D(*vector),
        depends_on,
        values,
    )


def test_GIVEN_unrecognised_dtype_WHEN_parsing_dtype_THEN_parse_dtype_returns_empty_string(
    transformation_reader,
):
    n_warnings = len(transformation_reader.warnings)

    assert not transformation_reader._parse_dtype("notvalid", "TransformationName")
    assert len(transformation_reader.warnings) == n_warnings + 1
    assert "dtype" in transformation_reader.warnings[-1]


@pytest.mark.parametrize("dtype", ["double", "Double", "DOUBLE"])
def test_GIVEN_different_types_of_double_WHEN_parsing_dtype_THEN_parse_dtype_returns_same_value(
    transformation_reader, dtype
):
    assert transformation_reader._parse_dtype(dtype, "TransformationName") == "double"


def test_GIVEN_unrecognised_transformation_type_WHEN_parsing_transformation_type_THEN_parse_transformation_type_returns_empty_string(
    transformation_reader,
):
    n_warnings = len(transformation_reader.warnings)

    assert not transformation_reader._parse_transformation_type(
        "notvalid", "TransformationName"
    )
    assert len(transformation_reader.warnings) == n_warnings + 1
    assert "transformation type" in transformation_reader.warnings[-1]


def test_GIVEN_invalid_dtype_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    transformation_json["children"][0]["dataset"]["type"] = "NotAType"
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_invalid_transformation_type_WHEN_attempting_to_create_transformations_THEN_create_transform_is_not_called(
    transformation_reader, transformation_json
):
    transformation_json["children"][0]["attributes"][1]["values"] = "NotAType"
    transformation_reader._create_transformations(transformation_json["children"])

    transformation_reader.parent_component._create_and_add_transform.assert_not_called()


def test_GIVEN_transformation_has_depends_on_chain_WHEN_getting_depends_on_value_THEN_path_string_is_stored_in_dictionary(
    transformation_reader, transformation_json
):
    depends_on_path = "entry/instrument/component/transformations/transformation1"
    transformation_json["children"][0][
        "name"
    ] = transformation_name = "TransformationName"
    transformation_json["children"][0]["attributes"][3]["values"] = depends_on_path
    transformation_reader._create_transformations(transformation_json["children"])

    assert (
        transformation_reader.depends_on_paths[transformation_name] == depends_on_path
    )


@pytest.mark.parametrize("depends_on_path", [".", None])
def test_GIVEN_transformation_has_no_depends_on_chain_WHEN_getting_depends_on_value_THEN_path_string_isnt_stored_in_dictionary(
    transformation_reader, transformation_json, depends_on_path
):
    transformation_json["children"][0]["attributes"][3]["values"] = depends_on_path
    transformation_reader._create_transformations(transformation_json["children"])

    assert len(transformation_reader.depends_on_paths) == 0
