import os
import h5py
from nexus_constructor.component_type import make_dictionary_of_class_definitions
from nexus_constructor.nexus import nexus_wrapper as nx
from nexus_constructor.component import ComponentModel


class Instrument:
    def __init__(self, nexus_file: nx.NexusWrapper):
        self.nexus = nexus_file
        self.nx_classes = make_dictionary_of_class_definitions(
            os.path.abspath(os.path.join(os.curdir, "definitions"))
        )

    def add_component(self, name: str, nx_class: str, description: str, geometry):
        """
        Creates a component group in a NeXus file
        :param name: Name of the component group to create
        :param nx_class: NX_class of the component group to create
        :param description: Description of the component
        :param geometry: geometry model
        """
        parent_group = self.nexus.instrument
        if nx_class == "NXmonitor":
            parent_group = self.nexus.entry
        component_group = self.nexus.create_nx_group(name, nx_class, parent_group)
        component = ComponentModel(self.nexus, component_group)
        component.description = description

    def remove_component(self):
        raise NotImplementedError("Instrument.remove_component() not yet implemented")

    def get_component_list(self):
        component_list = []

        def find_components(_, node):
            if isinstance(node, h5py.Group):
                if "NX_class" in node.attrs.keys():
                    if node.attrs["NX_class"] in self.nx_classes:
                        component_list.append(ComponentModel(self.nexus, node))

        self.nexus.nexus_file.visititems(find_components)
        return component_list
