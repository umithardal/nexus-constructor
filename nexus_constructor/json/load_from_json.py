import json

from PySide2.QtWidgets import QWidget

from nexus_constructor.component.component_type import COMPONENT_TYPES
from nexus_constructor.json.load_from_json_utils import (
    _find_nx_class,
    _find_attribute_from_list_or_dict,
    DEPENDS_ON_IGNORE,
)
from nexus_constructor.json.transformation_reader import TransformationReader
from nexus_constructor.model.component import Component
from nexus_constructor.model.entry import Entry
from nexus_constructor.model.instrument import Instrument
from nexus_constructor.model.transformation import Transformation
from nexus_constructor.ui_utils import show_warning_dialog

NX_INSTRUMENT = "NXinstrument"
NX_SAMPLE = "NXsample"


def _retrieve_children_list(json_dict: dict) -> list:
    """
    Attempts to retrieve the children from the JSON dictionary.
    :param json_dict: The JSON dictionary loaded by the user.
    :return: The children value is returned if it was found, otherwise an empty list is returned.
    """
    try:
        entry = json_dict["nexus_structure"]["children"][0]
        return entry["children"]
    except (KeyError, IndexError, TypeError):
        return []


def _get_transformation_by_name(
    component: Component, transformation_name: str
) -> Transformation:
    for transformation in component.transforms_list:
        if transformation.name == transformation_name:
            return transformation


def _connect_dependencies(component: Component, transformation: Transformation):
    component.depends_on = transformation


class JSONReader:
    def __init__(self, parent: QWidget):
        self.entry = Entry()
        self.entry.instrument = Instrument()
        self.parent = parent
        self.warnings = []
        self.depends_on_paths = dict()
        self.component_dictionary = dict()

    def load_model_from_json(self, filename: str) -> bool:
        """
        Tries to load a model from a JSON file.
        :param filename: The filename of the JSON file.
        :return: True if the model was loaded without problems, False otherwise.
        """
        with open(filename, "r") as json_file:

            json_data = json_file.read()

            try:
                json_dict = json.loads(json_data)
            except ValueError as exception:
                show_warning_dialog(
                    "Provided file not recognised as valid JSON",
                    "Invalid JSON",
                    f"{exception}",
                    self.parent,
                )
                return False

            children_list = _retrieve_children_list(json_dict)

            if not children_list:
                show_warning_dialog(
                    "Provided file not recognised as valid Instrument",
                    "Invalid JSON",
                    parent=self.parent,
                )
                return False

            for child in children_list:
                self._read_json_object(
                    child, json_dict["nexus_structure"]["children"][0].get("name")
                )

            for key in self.depends_on_paths.keys():

                depends_on_path = self.depends_on_paths[key].split("/")[3:]

                target_component_name = depends_on_path[0]
                target_transformation_name = depends_on_path[-1]

                # Assuming this is always a transformation
                self.component_dictionary[key].depends_on = _get_transformation_by_name(
                    self.component_dictionary[target_component_name],
                    target_transformation_name,
                )

            if self.warnings:
                show_warning_dialog(
                    "\n".join(self.warnings),
                    "Warnings encountered loading JSON",
                    parent=self.parent,
                )
                return True

            return True

    def _read_json_object(self, json_object: dict, parent_name: str = None):
        """
        Tries to create a component based on the contents of the JSON file.
        :param json_object:  A component from the JSON dictionary.
        """
        name = json_object.get("name")

        if name:

            nx_class = _find_nx_class(json_object.get("attributes"))

            if nx_class == NX_INSTRUMENT:
                return all(
                    [
                        self._read_json_object(child, name)
                        for child in json_object.get("children")
                    ]
                )

            if not self._validate_nx_class(name, nx_class):
                return

            if nx_class == NX_SAMPLE:
                component = self.entry.instrument.sample
                component.name = name
            else:
                component = Component(name)
                component.nx_class = nx_class
                self.entry.instrument.add_component(component)

            try:
                children = json_object["children"]
            except KeyError:
                return

            transformation_reader = TransformationReader(component, children)
            transformation_reader.add_transformations_to_component()
            self.warnings += transformation_reader.warnings

            depends_on_path = _find_attribute_from_list_or_dict("depends_on", children)

            if depends_on_path not in DEPENDS_ON_IGNORE:
                self.depends_on_paths[name] = depends_on_path

            self.component_dictionary[name] = component

        else:
            self.warnings.append(
                f"Unable to find object name for child of {parent_name}."
            )

    def _validate_nx_class(self, name: str, nx_class: str) -> bool:
        """
        Validates the NXclass by checking if it was found, and if it matches known NXclasses for components.
        :param nx_class: The NXclass string obtained from the dictionary.
        :return: True if the NXclass is valid, False otherwise.
        """
        if not nx_class:
            self.warnings.append(f"Unable to determine NXclass of component {name}.")
            return False

        if nx_class not in COMPONENT_TYPES:
            return False

        return True
