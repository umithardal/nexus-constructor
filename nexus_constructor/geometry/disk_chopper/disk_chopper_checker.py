import logging
from typing import Sequence, Dict, List

import numpy as np
from PySide2.QtWidgets import QListWidget

from nexus_constructor.field_widget import FieldWidget
from nexus_constructor.geometry.disk_chopper.chopper_details import ChopperDetails
from nexus_constructor.unit_utils import (
    units_are_recognised_by_pint,
    units_are_expected_dimensionality,
    units_have_magnitude_of_one,
)
from nexus_constructor.validators import VALUE_TYPE

SLIT_EDGES_NAME = "slit_edges"
SLITS_NAME = "slits"
RADIUS_NAME = "radius"
SLIT_HEIGHT_NAME = "slit_height"
NAME = "name"

UNABLE = "Unable to create chopper geometry - "
EXPECTED_TYPE_ERROR_MSG = {
    SLIT_EDGES_NAME: "float",
    SLITS_NAME: "int",
    RADIUS_NAME: "float",
    SLIT_HEIGHT_NAME: "float",
}

REQUIRED_CHOPPER_FIELDS = {SLIT_EDGES_NAME, SLITS_NAME, RADIUS_NAME, SLIT_HEIGHT_NAME}
INT_TYPES = [key for key in VALUE_TYPE.keys() if "int" in str(VALUE_TYPE[key])]
FLOAT_TYPES = [key for key in VALUE_TYPE.keys() if "float" in str(VALUE_TYPE[key])]

UNITS_REQUIRED = [RADIUS_NAME, SLIT_EDGES_NAME, SLIT_HEIGHT_NAME]
EXPECTED_UNIT_TYPE = {
    RADIUS_NAME: "millimetres",
    SLIT_EDGES_NAME: "degrees",
    SLIT_HEIGHT_NAME: "millimetres",
}


def _incorrect_data_type_message(
    data_dict: dict, field_name: str, expected_type: str
) -> str:
    """
    Creates a string explaining to the user that the field input did not have the expected type.
    :param data_dict: The dictionary containing the different data fields for the disk chopper.
    :param field_name: The name of the field that failed the check.
    :param expected_type: The expected data type.
    :return: A string that contains the name of the field, the type it should have, and the type the user entered.
    """
    return (
        f"Wrong {field_name} type. Expected {expected_type} but found"
        f" {type(data_dict[field_name])}."
    )


def _edges_array_has_correct_shape(edges_dim: int, edges_shape: tuple) -> bool:
    """
    Checks that the edges array consists of either one row or one column.
    :param edges_dim: The number of dimensions in the slit edges array.
    :param edges_shape: The shape of the slit edges array.
    :return: True if the edges array is 1D. False otherwise.
    """
    if edges_dim > 2:
        logging.info(
            f"{UNABLE} Expected slit edges array to be 1D but it has {edges_dim}"
            " dimensions."
        )
        return False

    if edges_dim == 2:
        if edges_shape[0] != 1 and edges_shape[1] != 1:
            logging.info(
                f"{UNABLE} Expected slit edges array to be 1D but it has shape"
                f" {edges_shape}."
            )
            return False

    return True


def _units_are_valid(units_dict: dict) -> bool:
    """
    Checks that the units for the slit edges, radius, and slit height are valid.
    :param units_dict: The dictionary of units for the slit edges, radius, and slit height.
    :return: True if the units are all valid, False otherwise.
    """
    good_units = True

    for field in UNITS_REQUIRED:
        unit_input = units_dict[field]

        if not units_are_recognised_by_pint(unit_input, False):
            logging.info(
                f"{UNABLE} Units for {field} are not recognised. Found value:"
                f" {unit_input}"
            )
            good_units = False
            continue
        if not units_are_expected_dimensionality(
            unit_input, EXPECTED_UNIT_TYPE[field], False
        ):
            logging.info(
                f"{UNABLE} Units for {field} have wrong type. Found {unit_input} but"
                " expected something that can be converted to"
                f" {EXPECTED_UNIT_TYPE[field]}."
            )
            good_units = False
            continue
        if not units_have_magnitude_of_one(unit_input, False):
            logging.info(
                f"{UNABLE} Units for {field} should have a magnitude of one. Found"
                f" value: {unit_input}"
            )
            good_units = False

    return good_units


def _input_describes_valid_chopper(
    chopper_details: ChopperDetails, slit_edges: Sequence
) -> bool:
    """
    A final check that the input has the following properties:
        - The length of the slit edges array is twice the number of slits
        - The slit height is smaller than the radius
        - The slit edges array is sorted.
        - The slit edges array doesn't contain repeated angles.
        - The slit edges array doesn't contain overlapping slits.
    If this is all true then a chopper mesh can be created.
    :param chopper_details: The Chopper Details object.
    :param slit_edges: The original slit edges array provided by the user/contained in the NeXus file that has not yet
        been converted to radians (though it may already be in radians). Used when logging errors about slit edges
        data so it's in a format the user recognises.
    :return: True if all the conditions above are met. False otherwise.
    """
    # Check that the number of slit edges is equal to two times the number of slits
    if len(chopper_details.slit_edges) != 2 * chopper_details.slits:
        logging.info(
            f"{UNABLE} Size of slit edges array should be twice the number of slits."
            f" Instead there are {chopper_details.slits} slits and"
            f" {len(chopper_details.slit_edges)} slit edges."
        )
        return False

    # Check that the slit height is smaller than the radius
    if chopper_details.slit_height >= chopper_details.radius:
        logging.info(
            f"{UNABLE} Slit height should be smaller than radius. Instead slit height"
            f" is {chopper_details.slit_height} metres and radius is"
            f" {chopper_details.radius} metres."
        )
        return False

    # Check that the list of slit edges is sorted
    if not (np.diff(slit_edges) >= 0).all():
        logging.info(
            f"{UNABLE} Slit edges array is not sorted. Found values: {slit_edges}"
        )
        return False

    # Check that there are no repeated angles
    if len(slit_edges) != len(np.unique(slit_edges)):
        logging.info(
            f"{UNABLE} Angles in slit edges array should be unique. Found values:"
            f" {slit_edges}"
        )
        return False

    # Check that the first and last edges do not overlap
    if (chopper_details.slit_edges != sorted(chopper_details.slit_edges)) and (
        chopper_details.slit_edges[-1] >= chopper_details.slit_edges[0]
    ):
        logging.info(
            f"{UNABLE} Slit edges contains overlapping slits. Found values:"
            f" {slit_edges}"
        )
        return False

    return True


class UserDefinedChopperChecker:
    def __init__(
        self, fields_widget: QListWidget, fields_dict: Dict[str, FieldWidget] = dict()
    ):

        self.fields_dict = fields_dict
        self.units_dict = {}
        self.converted_values = {}
        self._chopper_details = None

        for i in range(fields_widget.count()):
            widget = fields_widget.itemWidget(fields_widget.item(i))
            self.fields_dict[widget.name] = widget

    def _check_data_type(self, field: str, expected_types: List[str],) -> bool:
        # if isinstance(field_widget, np.int64):
        #     # Fix for windows - for some reason int64 is the default numpy int type on windows...
        #     dtype = np.int32
        if self.fields_dict[field].dtype not in expected_types:
            return False

        try:
            self.converted_values[field] = VALUE_TYPE[self.fields_dict[field].dtype](
                self.fields_dict[field].value.values
            )
        except Exception:
            return False
        return True

    def _data_has_correct_type(self) -> bool:
        """
        Checks that the data required to create a Chopper mesh have the expected types.
        :param fields_dict: The dictionary of field names and their field widgets/NeXus data.
        :return: True if all the fields have the correct types, False otherwise.
        """
        correct_slits_type = self._check_data_type(SLITS_NAME, INT_TYPES)
        correct_radius_type = self._check_data_type(
            RADIUS_NAME, FLOAT_TYPES + INT_TYPES,
        )
        correct_slit_height_type = self._check_data_type(
            SLIT_HEIGHT_NAME, FLOAT_TYPES + INT_TYPES,
        )
        correct_slit_edges_type = self._check_data_type(
            SLIT_EDGES_NAME, FLOAT_TYPES + INT_TYPES,
        )

        if (
            correct_slits_type
            and correct_radius_type
            and correct_slit_height_type
            and correct_slit_edges_type
        ):
            return True

        problems = []

        if not correct_slits_type:
            problems.append(
                _incorrect_data_type_message(
                    self.fields_dict, SLITS_NAME, EXPECTED_TYPE_ERROR_MSG[SLITS_NAME]
                )
            )

        if not correct_radius_type:
            problems.append(
                _incorrect_data_type_message(
                    self.fields_dict, RADIUS_NAME, EXPECTED_TYPE_ERROR_MSG[RADIUS_NAME]
                )
            )

        if not correct_slit_height_type:
            problems.append(
                _incorrect_data_type_message(
                    self.fields_dict,
                    SLIT_HEIGHT_NAME,
                    EXPECTED_TYPE_ERROR_MSG[SLIT_HEIGHT_NAME],
                )
            )

        if not correct_slit_edges_type:
            problems.append(
                _incorrect_data_type_message(
                    self.fields_dict,
                    SLIT_EDGES_NAME,
                    EXPECTED_TYPE_ERROR_MSG[SLIT_EDGES_NAME],
                )
            )

        logging.info(f"{UNABLE}\n{problems}")
        return False

    @property
    def chopper_details(self) -> ChopperDetails:
        """
        :return: The ChopperDetails object of the user-defined disk chopper.
        """
        return self._chopper_details

    def required_fields_present(self) -> bool:
        """
        Checks that all of the fields and attributes required to create the disk chopper are present.
        :return: True if all the required fields are present, False otherwise.
        """
        missing_fields = REQUIRED_CHOPPER_FIELDS - self.fields_dict.keys()

        if len(missing_fields) > 0:
            logging.info(
                f"{UNABLE} Required field(s) missing:", ", ".join(missing_fields)
            )
            return False

        missing_units = []

        for field in UNITS_REQUIRED:
            units = self.fields_dict[field].units

            if not units:
                missing_units.append(field)
            else:
                self.units_dict[field] = units

        print(self.units_dict)

        if len(missing_units) > 0:
            logging.info(
                f"{UNABLE} Units are missing from field(s):", ", ".join(missing_units)
            )
            return False

        return True

    def validate_chopper(self) -> bool:
        """
        Performs the following checks in order to determine if the chopper input is valid: 1) Checks that the required
        fields are present, 2) Checks that the fields have the correct type, 3) Checks that the slit edges array is 1D,
        and 4) Checks that the overall chopper geometry is valid (no overlapping slits, repeated angles, etc).
        :return: True if the chopper is valid, False otherwise.
        """
        if not (
            self.required_fields_present()
            and self._data_has_correct_type()
            and _units_are_valid(self.units_dict)
            and _edges_array_has_correct_shape(
                self.fields_dict[SLIT_EDGES_NAME].value.values.ndim,
                self.fields_dict[SLIT_EDGES_NAME].value.values.shape,
            )
        ):
            return False

        self._chopper_details = ChopperDetails(
            self.converted_values[SLITS_NAME],
            self.converted_values[SLIT_EDGES_NAME],
            self.converted_values[RADIUS_NAME],
            self.converted_values[SLIT_HEIGHT_NAME],
            self.units_dict[SLIT_EDGES_NAME],
            self.units_dict[SLIT_HEIGHT_NAME],
            self.units_dict[RADIUS_NAME],
        )

        return _input_describes_valid_chopper(
            self._chopper_details, self.fields_dict[SLIT_EDGES_NAME].value.values
        )
