from geometry_constructor.data_model import OFFGeometry, PixelData, PixelGrid, Vector
from PySide2.Qt3DRender import Qt3DRender
from PySide2.QtGui import QVector3D
import struct


# Basing off a C++ custom mesh implementation at:
# https://github.com/iLya84a/qt3d/blob/master/custom-mesh-qml/CustomMesh.cpp
# and a PyQt5 example can be found at:
# https://github.com/geehalel/npindi/blob/57c092200dd9cb259ac1c730a1258a378a1a6342/apps/mount3D/world3D-starspheres.py#L86


class QtOFFGeometry(Qt3DRender.QGeometry):

    def __init__(self, model: OFFGeometry, pixel_data: PixelData, parent=None):
        super().__init__(parent)

        if isinstance(pixel_data, PixelGrid):
            faces, vertices = self.repeat_shape_over_grid(model, pixel_data)
        else:
            faces = model.faces
            vertices = model.vertices

        # for each point in each triangle in each face, add its points to the vertices list
        vertex_buffer_values = []
        for face in faces:
            for i in range(len(face) - 2):
                for point_index in [face[0], face[i + 1], face[i + 2]]:
                    vertex = vertices[point_index]
                    vertex_buffer_values.append(vertex.x)
                    vertex_buffer_values.append(vertex.y)
                    vertex_buffer_values.append(vertex.z)
                # repeat with the opposite winding to ensure the face is rendered regardless of winding in loaded model
                for point_index in [face[0], face[i + 2], face[i + 1]]:
                    vertex = vertices[point_index]
                    vertex_buffer_values.append(vertex.x)
                    vertex_buffer_values.append(vertex.y)
                    vertex_buffer_values.append(vertex.z)

        normal_buffer_values = []
        for face in faces:
            for i in range(len(face) - 2):
                p1 = vertices[face[0]]
                p2 = vertices[face[i + 1]]
                p3 = vertices[face[i + 2]]
                normal = QVector3D.normal(QVector3D(p1.x, p1.y, p1.z),
                                          QVector3D(p2.x, p2.y, p2.z),
                                          QVector3D(p3.x, p3.y, p3.z))
                for j in range(3):
                    normal_buffer_values.append(normal.x())
                    normal_buffer_values.append(normal.y())
                    normal_buffer_values.append(normal.z())
                # repeat with the opposite normal to ensure the face is rendered regardless of winding in loaded model
                for j in range(3):
                    normal_buffer_values.append(-normal.x())
                    normal_buffer_values.append(-normal.y())
                    normal_buffer_values.append(-normal.z())

        vertexBuffer = Qt3DRender.QBuffer(self)
        vertexBuffer.setData(
            struct.pack('%sf' % len(vertex_buffer_values), *vertex_buffer_values)
        )
        normalBuffer = Qt3DRender.QBuffer(self)
        normalBuffer.setData(
            struct.pack('%sf' % len(normal_buffer_values), *normal_buffer_values)
        )

        float_size = len(struct.pack('f', 0.0))

        positionAttribute = Qt3DRender.QAttribute(self)
        positionAttribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        positionAttribute.setBuffer(vertexBuffer)
        positionAttribute.setDataType(Qt3DRender.QAttribute.Float)
        positionAttribute.setDataSize(3)
        positionAttribute.setByteOffset(0)
        positionAttribute.setByteStride(3 * float_size)
        positionAttribute.setCount(len(vertex_buffer_values))
        positionAttribute.setName(Qt3DRender.QAttribute.defaultPositionAttributeName())

        normalAttribute = Qt3DRender.QAttribute(self)
        normalAttribute.setAttributeType(Qt3DRender.QAttribute.VertexAttribute)
        normalAttribute.setBuffer(normalBuffer)
        normalAttribute.setDataType(Qt3DRender.QAttribute.Float)
        normalAttribute.setDataSize(3)
        normalAttribute.setByteOffset(0)
        normalAttribute.setByteStride(3 * float_size)
        normalAttribute.setCount(len(normal_buffer_values))
        normalAttribute.setName(Qt3DRender.QAttribute.defaultNormalAttributeName())

        self.addAttribute(positionAttribute)
        self.addAttribute(normalAttribute)
        self.vertex_count = len(vertex_buffer_values) // 3

        print('Qt mesh built')

    def repeat_shape_over_grid(self, model: OFFGeometry, grid: PixelGrid):
        faces = []
        vertices = []
        for row in range(grid.rows):
            for col in range(grid.columns):
                faces += [
                    [i + (col + (row * grid.columns)) * len(model.vertices) for i in face]
                    for face in model.faces
                ]
                vertices += [
                    Vector(vec.x + (col * grid.col_width),
                           vec.y + (row * grid.row_height),
                           vec.z)
                    for vec in model.vertices
                ]
        return faces, vertices


class OffMesh(Qt3DRender.QGeometryRenderer):

    def __init__(self, geometry: OFFGeometry, pixel_data: PixelData=None, parent=None):
        super().__init__(parent)

        qt_geometry = QtOFFGeometry(geometry, pixel_data, self)

        self.setInstanceCount(1)
        self.setFirstVertex(0)
        self.setFirstInstance(0)
        self.setPrimitiveType(Qt3DRender.QGeometryRenderer.Triangles)
        self.setGeometry(qt_geometry)
        self.setVertexCount(qt_geometry.vertex_count)
