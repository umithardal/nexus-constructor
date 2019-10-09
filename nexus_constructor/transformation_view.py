from ui.transformation import Ui_Transformation
from ui.link import Ui_Link
from PySide2.QtWidgets import QGroupBox, QFrame, QWidget
from PySide2.QtGui import QVector3D
from nexus_constructor.transformations import Transformation
from nexus_constructor.instrument import Instrument
from nexus_constructor.component_tree_model import LinkTransformation
from nexus_constructor.component import Component


class EditTransformation(QGroupBox):
    def __init__(self, parent: QWidget, transformation: Transformation):
        super().__init__(parent)
        self.transformation_frame = Ui_Transformation()
        self.transformation_frame.setupUi(self)
        self.transformation = transformation
        current_vector = self.transformation.vector
        self.transformation_frame.xSpinBox.setValue(current_vector.x())
        self.transformation_frame.ySpinBox.setValue(current_vector.y())
        self.transformation_frame.zSpinBox.setValue(current_vector.z())
        self.transformation_frame.nameLineEdit.setText(self.transformation.name)
        self.transformation_frame.valueSpinBox.setValue(self.transformation.value)
        self.disable()

    def disable(self):
        self.transformation_frame.xSpinBox.setEnabled(False)
        self.transformation_frame.ySpinBox.setEnabled(False)
        self.transformation_frame.zSpinBox.setEnabled(False)
        self.transformation_frame.valueSpinBox.setEnabled(False)
        self.transformation_frame.nameLineEdit.setEnabled(False)
        self.transformation_frame.editButton.setText("Edit")

    def enable(self):
        self.transformation_frame.xSpinBox.setEnabled(True)
        self.transformation_frame.ySpinBox.setEnabled(True)
        self.transformation_frame.zSpinBox.setEnabled(True)
        self.transformation_frame.valueSpinBox.setEnabled(True)
        self.transformation_frame.nameLineEdit.setEnabled(True)
        self.transformation_frame.editButton.setText("Done")

    def saveChanges(self):
        self.transformation.name = self.transformation_frame.nameLineEdit.text()
        self.transformation.vector = QVector3D(
            self.transformation_frame.xSpinBox.value(),
            self.transformation_frame.ySpinBox.value(),
            self.transformation_frame.zSpinBox.value(),
        )
        self.transformation.value = self.transformation_frame.valueSpinBox.value()


class EditTranslation(EditTransformation):
    def __init__(self, parent: QWidget, transformation: Transformation):
        super().__init__(parent, transformation)
        self.transformation_frame.valueLabel.setText("Position (m)")
        self.setTitle("Translation")


class EditRotation(EditTransformation):
    def __init__(self, parent: QWidget, transformation: Transformation):
        super().__init__(parent, transformation)
        self.transformation_frame.valueLabel.setText("Rotation (°)")
        self.setTitle("Rotation")

def links_back_to_component(reference: Component, comparison: Component):
    if reference == comparison:
        return True
    if not comparison.transforms.has_link:
        return False
    if comparison.transforms.link.component_link == None:
        return False
    return links_back_to_component(reference, comparison.transforms.link.component_link)

class EditTransformationLink(QFrame):
    def __init__(
        self, parent: QWidget, link: LinkTransformation, instrument: Instrument
    ):
        super().__init__(parent)
        self.link = link
        self.instrument = instrument
        self.link_frame = Ui_Link()
        self.link_frame.setupUi(self)
        self.populate_combo_box()

    def populate_combo_box(self):
        try:
            self.link_frame.TransformationsComboBox.currentIndexChanged.disconnect()
        except Exception:
            pass
        self.link_frame.TransformationsComboBox.clear()
        self.link_frame.TransformationsComboBox.addItem("(None)")
        self.link_frame.TransformationsComboBox.setCurrentIndex(0)
        components = self.instrument.get_component_list()
        for current_component in components:
            transformations = current_component.transforms
            self.link_frame.TransformationsComboBox.addItem(current_component.name, userData = current_component)
            last_index = self.link_frame.TransformationsComboBox.count() - 1

            if links_back_to_component(self.link.parent.parent_component, current_component):
                self.link_frame.TransformationsComboBox.model().item(last_index).setEnabled(False)
            if len(transformations) == 0:
                self.link_frame.TransformationsComboBox.model().item(last_index).setEnabled(False)
            if self.link.linked_component != None and self.link.linked_component == current_component:
                self.link_frame.TransformationsComboBox.setCurrentIndex(self.link_frame.TransformationsComboBox.count() - 1)
        self.link_frame.TransformationsComboBox.currentIndexChanged.connect(self.set_new_index)

    def set_new_index(self, new_index):
        if new_index == -1:
            return
        if new_index == 0:
            self.link.linked_component = None
            self.link.parent.parent_component.depends_on = None
            return
        current_component = self.link_frame.TransformationsComboBox.currentData()
        self.link.linked_component = current_component
        if len(self.link.parent) == 0:
            self.link.parent.parent_component.depends_on = current_component.transforms[0]
        else:
            self.link.parent.parent_component.depends_on = self.link.parent[0]
            self.link.parent[-1].depends_on = current_component.transforms[0]

    def enable(self):
        self.populate_combo_box()

    def saveChanges(self):
        pass
