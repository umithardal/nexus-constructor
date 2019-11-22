from PySide2.QtWidgets import (
    QAction,
    QToolBar,
    QAbstractItemView,
    QMainWindow,
    QApplication,
    QInputDialog,
)
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QLabel, QGridLayout, QComboBox, QPushButton

import silx.gui.hdf5
import os
import h5py

import nexus_constructor.json.forwarder_json_writer
from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.filewriter_command_dialog import FilewriterCommandDialog
from nexus_constructor.instrument import Instrument
from nexus_constructor.ui_utils import file_dialog, show_warning_dialog
from ui.main_window import Ui_MainWindow
from nexus_constructor.component.component import Component, TransformationsList
from nexus_constructor.transformations import Transformation

from nexus_constructor.component_tree_model import ComponentTreeModel
from nexus_constructor.component_tree_view import (
    ComponentEditorDelegate,
    LinkTransformation,
)
from nexus_constructor.json import filewriter_json_writer
from nexus_constructor.json.filewriter_json_reader import json_to_nexus

NEXUS_FILE_TYPES = {"NeXus Files": ["nxs", "nex", "nx5"]}
JSON_FILE_TYPES = {"JSON Files": ["json", "JSON"]}


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, instrument: Instrument, definitions_dir: str):
        super().__init__()
        self.instrument = instrument
        self.definitions_dir = definitions_dir

    def setupUi(self, main_window):
        super().setupUi(main_window)

        self.export_to_nexus_file_action.triggered.connect(self.save_to_nexus_file)
        self.open_nexus_file_action.triggered.connect(self.open_nexus_file)
        self.open_json_file_action.triggered.connect(self.open_json_file)
        self.export_to_filewriter_JSON_action.triggered.connect(
            self.save_to_filewriter_json
        )
        self.export_to_forwarder_JSON_action.triggered.connect(
            self.save_to_forwarder_json
        )

        # Clear the 3d view when closed
        QApplication.instance().aboutToQuit.connect(self.sceneWidget.delete)

        self.widget = silx.gui.hdf5.Hdf5TreeView()
        self.widget.setAcceptDrops(True)
        self.widget.setDragEnabled(True)
        self.treemodel = self.widget.findHdf5TreeModel()
        self.treemodel.setDatasetDragEnabled(True)
        self.treemodel.setFileDropEnabled(True)
        self.treemodel.setFileMoveEnabled(True)
        self.treemodel.insertH5pyObject(self.instrument.nexus.nexus_file)
        self.instrument.nexus.file_changed.connect(
            self.update_nexus_file_structure_view
        )
        self.silx_tab_layout.addWidget(self.widget)
        self.instrument.nexus.show_entries_dialog.connect(self.show_entries_dialog)

        self.instrument.nexus.component_added.connect(self.sceneWidget.add_component)
        self.instrument.nexus.component_removed.connect(
            self.sceneWidget.delete_component
        )
        self.instrument.nexus.transformation_changed.connect(
            self._update_transformations_3d_view
        )

        self.widget.setVisible(True)

        self._set_up_tree_view()
        self.set_up_warning_window()

    def _set_up_tree_view(self):
        self._set_up_component_model()
        self.component_tree_view.setDragEnabled(True)
        self.component_tree_view.setAcceptDrops(True)
        self.component_tree_view.setDropIndicatorShown(True)
        self.component_tree_view.header().hide()
        self.component_tree_view.updateEditorGeometries()
        self.component_tree_view.updateGeometries()
        self.component_tree_view.updateGeometry()
        self.component_tree_view.clicked.connect(self.on_clicked)
        self.component_tree_view.setSelectionMode(QAbstractItemView.SingleSelection)

        self.component_tool_bar = QToolBar("Actions", self.component_tree_view_tab)
        self.new_component_action = QAction(
            QIcon(os.path.join("ui", "new_component.png")),
            "New component",
            self.component_tree_view_tab,
        )
        self.new_component_action.triggered.connect(self.show_add_component_window)
        self.component_tool_bar.addAction(self.new_component_action)
        self.new_translation_action = QAction(
            QIcon(os.path.join("ui", "new_translation.png")),
            "New translation",
            self.component_tree_view_tab,
        )
        self.new_translation_action.triggered.connect(self.on_add_translation)
        self.new_translation_action.setEnabled(False)
        self.component_tool_bar.addAction(self.new_translation_action)
        self.new_rotation_action = QAction(
            QIcon(os.path.join("ui", "new_rotation.png")),
            "New rotation",
            self.component_tree_view_tab,
        )
        self.new_rotation_action.triggered.connect(self.on_add_rotation)
        self.new_rotation_action.setEnabled(False)
        self.component_tool_bar.addAction(self.new_rotation_action)
        self.create_link_action = QAction(
            QIcon(os.path.join("ui", "create_link.png")),
            "Create link",
            self.component_tree_view_tab,
        )
        self.create_link_action.triggered.connect(self.on_create_link)
        self.create_link_action.setEnabled(False)
        self.component_tool_bar.addAction(self.create_link_action)
        self.duplicate_action = QAction(
            QIcon(os.path.join("ui", "duplicate.png")),
            "Duplicate",
            self.component_tree_view_tab,
        )
        self.component_tool_bar.addAction(self.duplicate_action)
        self.duplicate_action.triggered.connect(self.on_duplicate_node)
        self.duplicate_action.setEnabled(False)

        self.edit_component_action = QAction(
            QIcon(os.path.join("ui", "edit_component.png")),
            "Edit Component",
            self.component_tree_view_tab,
        )
        self.edit_component_action.setEnabled(False)
        self.edit_component_action.triggered.connect(self.show_edit_component_dialog)
        self.component_tool_bar.addAction(self.edit_component_action)

        self.delete_action = QAction(
            QIcon(os.path.join("ui", "delete.png")),
            "Delete",
            self.component_tree_view_tab,
        )
        self.delete_action.triggered.connect(self.on_delete_item)
        self.delete_action.setEnabled(False)
        self.component_tool_bar.addAction(self.delete_action)
        self.componentsTabLayout.insertWidget(0, self.component_tool_bar)

    def _set_up_component_model(self):
        self.component_model = ComponentTreeModel(self.instrument)
        self.component_delegate = ComponentEditorDelegate(
            self.component_tree_view, self.instrument
        )
        self.component_tree_view.setItemDelegate(self.component_delegate)
        self.component_tree_view.setModel(self.component_model)

    def show_edit_component_dialog(self):
        selected_component = self.component_tree_view.selectedIndexes()[
            0
        ].internalPointer()
        self.show_add_component_window(selected_component)

    def show_entries_dialog(self, map_of_entries: dict, nexus_file: h5py.File):
        """
        Shows the entries dialog when loading a nexus file if there are multiple entries.
        :param map_of_entries: A map of the entry groups, with the key being the name of the group and value being the actual h5py group object.
        :param nexus_file: A reference to the nexus file.
        """
        self.entries_dialog = QDialog()
        self.entries_dialog.setMinimumWidth(400)
        self.entries_dialog.setWindowTitle(
            "Multiple Entries found. Please choose the entry name from the list."
        )
        combo = QComboBox()

        # Populate the combo box with the names of the entry groups.
        [combo.addItem(x) for x in map_of_entries.keys()]
        ok_button = QPushButton()

        ok_button.setText("OK")
        ok_button.clicked.connect(self.entries_dialog.close)

        def _load_current_entry():
            self.instrument.nexus.load_file(
                map_of_entries[combo.currentText()], nexus_file
            )
            self._set_up_component_model()
            self._update_views()

        # Connect the clicked signal of the ok_button to instrument.load_file and pass the file and entry group object.
        ok_button.clicked.connect(_load_current_entry)

        self.entries_dialog.setLayout(QGridLayout())

        self.entries_dialog.layout().addWidget(QLabel("Entry:"))
        self.entries_dialog.layout().addWidget(combo)
        self.entries_dialog.layout().addWidget(ok_button)
        self.entries_dialog.show()

    def set_button_state(self):
        indices = self.component_tree_view.selectedIndexes()
        if len(indices) == 0 or len(indices) != 1:
            self.delete_action.setEnabled(False)
            self.duplicate_action.setEnabled(False)
            self.new_rotation_action.setEnabled(False)
            self.new_translation_action.setEnabled(False)
            self.create_link_action.setEnabled(False)
        else:
            selected_object = indices[0].internalPointer()
            if isinstance(selected_object, Component) or isinstance(
                selected_object, Transformation
            ):
                self.delete_action.setEnabled(True)
                self.duplicate_action.setEnabled(True)
                self.edit_component_action.setEnabled(True)
            else:
                self.delete_action.setEnabled(False)
                self.duplicate_action.setEnabled(False)
                self.edit_component_action.setEnabled(False)
            if isinstance(selected_object, LinkTransformation):
                self.new_rotation_action.setEnabled(False)
                self.new_translation_action.setEnabled(False)
                self.delete_action.setEnabled(True)
            else:
                self.new_rotation_action.setEnabled(True)
                self.new_translation_action.setEnabled(True)

            if isinstance(selected_object, Component):
                if not hasattr(selected_object, "stored_transforms"):
                    selected_object.stored_transforms = selected_object.transforms
                if not selected_object.stored_transforms.has_link:
                    self.create_link_action.setEnabled(True)
                else:
                    self.create_link_action.setEnabled(False)
            elif isinstance(selected_object, TransformationsList):
                if not selected_object.has_link:
                    self.create_link_action.setEnabled(True)
                else:
                    self.create_link_action.setEnabled(False)
            elif isinstance(selected_object, Transformation):
                if not selected_object.parent.has_link:
                    self.create_link_action.setEnabled(True)
                else:
                    self.create_link_action.setEnabled(False)
            else:
                self.create_link_action.setEnabled(False)

    def on_create_link(self):
        selected = self.component_tree_view.selectedIndexes()
        if len(selected) > 0:
            self.component_model.add_link(selected[0])
            self.expand_transformation_list(selected[0])
            self.set_button_state()

    def on_clicked(self, index):
        self.set_button_state()

    def on_duplicate_node(self):
        selected = self.component_tree_view.selectedIndexes()
        if len(selected) > 0:
            self.component_model.duplicate_node(selected[0])
            self.expand_transformation_list(selected[0])

    def expand_transformation_list(self, node):
        current_pointer = node.internalPointer()
        if isinstance(current_pointer, TransformationsList) or isinstance(
            current_pointer, Component
        ):
            self.component_tree_view.expand(node)
            if isinstance(current_pointer, Component):
                trans_list_index = self.component_model.index(1, 0, node)
                self.component_tree_view.expand(trans_list_index)
            else:
                component_index = self.component_model.parent(node)
                self.component_tree_view.expand(component_index)
        elif isinstance(current_pointer, Transformation):
            trans_list_index = self.component_model.parent(node)
            self.component_tree_view.expand(trans_list_index)
            component_index = self.component_model.parent(trans_list_index)
            self.component_tree_view.expand(component_index)

    def add_transformation(self, transformation_type):
        selected = self.component_tree_view.selectedIndexes()
        if len(selected) > 0:
            current_index = selected[0]
            if transformation_type == "translation":
                self.component_model.add_translation(current_index)
            elif transformation_type == "rotation":
                self.component_model.add_rotation(current_index)
            else:
                raise ValueError(f"Unknown transformation type: {transformation_type}")
            self.expand_transformation_list(current_index)

    def on_add_translation(self):
        self.add_transformation("translation")

    def on_add_rotation(self):
        self.add_transformation("rotation")

    def set_up_warning_window(self):
        """
        Sets up the warning dialog that is shown when the definitions submodule has not been cloned.
        :return:
        """

        # Will contain .git even if missing so check that it does not contain just that file.
        if (
            not os.path.exists(self.definitions_dir)
            or len(os.listdir(self.definitions_dir)) <= 1
        ):
            show_warning_dialog(
                "Warning: NeXus definitions are missing. Did you forget to clone the submodules?\n run git submodule update --init ",
                title="NeXus definitions missing",
                parent=self,
            )

    def update_nexus_file_structure_view(self, nexus_file):
        self.treemodel.clear()
        self.treemodel.insertH5pyObject(nexus_file)

    def save_to_nexus_file(self):
        filename = file_dialog(True, "Save Nexus File", NEXUS_FILE_TYPES)
        self.instrument.nexus.save_file(filename)

    def save_to_filewriter_json(self):
        filename = file_dialog(True, "Save Filewriter JSON File", JSON_FILE_TYPES)
        if filename:
            dialog = FilewriterCommandDialog()
            dialog.exec_()
            nexus_file_name, broker, start_time, stop_time, service_id, abort_on_uninitialised_stream, use_swmr = (
                dialog.get_arguments()
            )
            with open(filename, "w") as file:
                filewriter_json_writer.generate_json(
                    self.instrument,
                    file,
                    nexus_file_name=nexus_file_name,
                    broker=broker,
                    streams=self.instrument.get_streams(),
                    links=self.instrument.get_links(),
                    start_time=start_time,
                    stop_time=stop_time,
                    service_id=service_id,
                    abort_uninitialised=abort_on_uninitialised_stream,
                    use_swmr=use_swmr,
                )

    def save_to_forwarder_json(self):
        filename = file_dialog(True, "Save Forwarder JSON File", JSON_FILE_TYPES)
        if filename:
            provider_type, ok_pressed = QInputDialog.getItem(
                None,
                "Provider type",
                "Select provider type for PVs",
                ["ca", "pva"],
                0,
                False,
            )
            if ok_pressed:
                with open(filename, "w") as file:
                    nexus_constructor.json.forwarder_json_writer.generate_forwarder_command(
                        file,
                        streams=self.instrument.get_streams(),
                        provider_type=provider_type,
                    )

    def open_nexus_file(self):
        filename = file_dialog(False, "Open Nexus File", NEXUS_FILE_TYPES)
        existing_file = self.instrument.nexus.nexus_file
        if self.instrument.nexus.open_file(filename):
            self._update_views()
            existing_file.close()

    def open_json_file(self):
        filename = file_dialog(False, "Open File Writer JSON File", JSON_FILE_TYPES)
        if filename:
            with open(filename, "r") as json_file:
                json_data = json_file.read()

                try:
                    nexus_file = json_to_nexus(json_data)
                except Exception as exception:
                    show_warning_dialog(
                        "Provided file not recognised as valid JSON",
                        "Invalid JSON",
                        f"{exception}",
                        parent=self,
                    )
                    return

                existing_file = self.instrument.nexus.nexus_file
                if self.instrument.nexus.load_nexus_file(nexus_file):
                    self._update_views()
                    existing_file.close()

    def _update_transformations_3d_view(self):
        self.sceneWidget.clear_all_transformations()
        for component in self.instrument.get_component_list():
            if component.name != "sample":
                self.sceneWidget.add_transformation(component.name, component.transform)

    def _update_views(self):
        self.sceneWidget.clear_all_transformations()
        self.sceneWidget.clear_all_components()
        self._update_3d_view_with_component_shapes()
        self._set_up_component_model()

    def _update_3d_view_with_component_shapes(self):
        for component in self.instrument.get_component_list():
            shape, positions = component.shape
            self.sceneWidget.add_component(component.name, shape, positions)
            self.sceneWidget.add_transformation(component.name, component.transform)

    def show_add_component_window(self, component: Component = None):
        self.add_component_window = QDialog()
        self.add_component_window.ui = AddComponentDialog(
            self.instrument,
            self.component_model,
            component,
            definitions_dir=self.definitions_dir,
            parent=self,
        )
        self.add_component_window.ui.setupUi(self.add_component_window)
        self.add_component_window.show()

    def on_delete_item(self):
        selected = self.component_tree_view.selectedIndexes()
        for item in selected:
            self.component_model.remove_node(item)
        self.set_button_state()