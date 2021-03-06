import uuid
from typing import Dict
import json

from PySide2.QtCore import QSettings
from PySide2.QtWidgets import (
    QMainWindow,
    QApplication,
    QAction,
    QMessageBox,
    QDialog,
    QInputDialog,
)
from nexusutils.nexusbuilder import NexusBuilder

from nexus_constructor.add_component_window import AddComponentDialog
from nexus_constructor.model.component import Component
from nexus_constructor.json.load_from_json import JSONReader
from nexus_constructor.ui_utils import file_dialog, show_warning_dialog
from nexus_constructor.model.model import Model
from nexus_constructor.create_forwarder_config import create_forwarder_config
from ui.main_window import Ui_MainWindow


NEXUS_FILE_TYPES = {"NeXus Files": ["nxs", "nex", "nx5"]}
JSON_FILE_TYPES = {"JSON Files": ["json", "JSON"]}
FLATBUFFER_FILE_TYPES = {"FlatBuffer Files": ["flat", "FLAT"]}


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, model: Model, nx_classes: Dict):
        super().__init__()
        self.model = model
        self.nx_classes = nx_classes

    def setupUi(self, main_window):
        super().setupUi(main_window)

        self.export_to_nexus_file_action.triggered.connect(self.save_to_nexus_file)
        self.open_nexus_file_action.triggered.connect(self.open_nexus_file)
        self.open_json_file_action.triggered.connect(self.open_json_file)
        self.open_idf_file_action.triggered.connect(self.open_idf_file)
        self.export_to_filewriter_JSON_action.triggered.connect(
            self.save_to_filewriter_json
        )
        self.export_to_forwarder_config_action.triggered.connect(
            self.save_to_forwarder_config
        )

        # Clear the 3d view when closed
        QApplication.instance().aboutToQuit.connect(self.sceneWidget.delete)

        # self.treemodel = self.widget.findHdf5TreeModel()
        # self.treemodel.setDatasetDragEnabled(True)
        # self.treemodel.setFileDropEnabled(True)
        # self.treemodel.setFileMoveEnabled(True)
        # self.treemodel.insertH5pyObject(self.model.signals.nexus_file)
        self.model.signals.file_changed.connect(self.update_nexus_file_structure_view)

        self.model.signals.component_added.connect(self.sceneWidget.add_component)
        self.model.signals.component_removed.connect(self.sceneWidget.delete_component)
        self.component_tree_view_tab.set_up_model(self.model)
        self.model.signals.transformation_changed.connect(
            self._update_transformations_3d_view
        )

        self._set_up_file_writer_control_window(main_window)
        self.file_writer_control_window = None
        self._update_views()

    def _set_up_file_writer_control_window(self, main_window):
        try:
            import confluent_kafka  # noqa: F401

            self.control_file_writer_action = QAction(main_window)
            self.control_file_writer_action.setText("Control file-writer")
            self.file_menu.addAction(self.control_file_writer_action)
            self.control_file_writer_action.triggered.connect(
                self.show_control_file_writer_window
            )
        except ImportError:
            pass

    def show_control_file_writer_window(self):
        if self.file_writer_control_window is None:
            from nexus_constructor.file_writer_ctrl_window import FileWriterCtrl

            self.file_writer_ctrl_window = FileWriterCtrl(
                self.model, QSettings("ess", "nexus-constructor")
            )
            self.file_writer_ctrl_window.show()

    def show_edit_component_dialog(self):
        selected_component = self.component_tree_view_tab.component_tree_view.selectedIndexes()[
            0
        ].internalPointer()
        self.show_add_component_window(selected_component)

    def update_nexus_file_structure_view(self, nexus_file):
        self.treemodel.clear()
        self.treemodel.insertH5pyObject(nexus_file)

    def save_to_nexus_file(self):
        filename = file_dialog(True, "Save Nexus File", NEXUS_FILE_TYPES)
        self.model.signals.save_file(filename)

    def open_idf_file(self):
        filename = file_dialog(False, "Open IDF file", {"IDF files": ["xml"]})
        self._load_idf(filename)

    def _load_idf(self, filename):
        try:
            builder = NexusBuilder(
                str(uuid.uuid4()),
                idf_file=filename,
                file_in_memory=True,
                nx_entry_name="entry",
            )
            builder.add_instrument_geometry_from_idf()
            self.model.signals.load_nexus_file(builder.target_file)
            self._update_views()
            QMessageBox.warning(
                self,
                "Mantid IDF loaded",
                "Please manually check the instrument for accuracy.",
            )
        except Exception:
            QMessageBox.critical(self, "IDF Error", "Error whilst loading IDF file")

    def save_to_filewriter_json(self):
        filename = file_dialog(True, "Save Filewriter JSON File", JSON_FILE_TYPES)

        if filename:
            with open(filename, "w") as file:
                json.dump(self.model.as_dict(), file, indent=2)

    def save_to_forwarder_config(self):
        filename = file_dialog(
            True, "Save Forwarder FlatBuffer File", FLATBUFFER_FILE_TYPES
        )
        if filename:
            provider_type, ok_pressed = QInputDialog.getItem(
                self,
                "Provider type",
                "Select provider type for PVs",
                ["ca", "pva", "fake"],
                0,
                False,
            )
            if ok_pressed:
                with open(filename, "wb") as flat_file:
                    flat_file.write(create_forwarder_config(self.model, provider_type,))

    def open_nexus_file(self):
        raise NotImplementedError

    def open_json_file(self):
        filename = file_dialog(False, "Open File Writer JSON File", JSON_FILE_TYPES)
        if filename:
            reader = JSONReader()
            success = reader.load_model_from_json(filename)
            if reader.warnings:
                show_warning_dialog(
                    "\n".join(reader.warnings),
                    "Warnings encountered loading JSON",
                    parent=self,
                )
            if success:
                self.model.entry = reader.entry
                self._update_views()

    def _update_transformations_3d_view(self):
        self.sceneWidget.clear_all_transformations()
        for component in self.model.entry.instrument.get_component_list():
            self.sceneWidget.add_transformation(component.name, component.qtransform)

    def _update_views(self):
        self.sceneWidget.clear_all_transformations()
        self.sceneWidget.clear_all_components()
        self.component_tree_view_tab.set_up_model(self.model)
        self._update_3d_view_with_component_shapes()

    def _update_3d_view_with_component_shapes(self):
        for component in self.model.entry.instrument.get_component_list():
            shape, positions = component.shape
            self.sceneWidget.add_component(component.name, shape, positions)
            self.sceneWidget.add_transformation(component.name, component.qtransform)

    def show_add_component_window(self, component: Component = None):
        self.add_component_window = QDialog()
        self.add_component_window.ui = AddComponentDialog(
            self.model,
            self.component_tree_view_tab.component_model,
            component,
            nx_classes=self.nx_classes,
            parent=self,
        )
        self.add_component_window.ui.setupUi(self.add_component_window)
        self.add_component_window.show()
