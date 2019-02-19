pragma Singleton
import QtQuick 2.0
QtObject {
    // Booleans to indicate that the units provided for loading a geometry or creating a cylinder were valid
    property bool validMeshUnits: false
    property bool validCylinderUnits: false
    property bool cylinderUnitMessage: false
}