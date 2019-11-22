from nexus_constructor.component.component import Component
from nexus_constructor.pixel_data import PixelGrid, PixelMapping, CountDirection, Corner
from typing import List


def geometry_group_name(component: Component):
    """
    Returns the name the component's geometry group should have

    For NXdetector groups:
        'detector_shape' if NXoff_geometry containing 'detector_faces', or NXcylindrical_geometry containing
    'detector_number'. 'pixel_shape' otherwise
    For other groups:
        'shape'
    """
    if component.nx_class == "Detector":
        if isinstance(component.pixel_data, PixelMapping):
            return "detector_shape"
        else:
            return "pixel_shape"
    else:
        return "shape"


class NexusDecoder:
    @staticmethod
    def unwound_off_faces(wound_faces, face_indices):
        """
        Returns a list of face point index lists, to be used as OFFGeometry.faces

        :param wound_faces: flattened list of face indices made from OFFGeometry.faces
        :param face_indices: indexes in wound_faces at which each face in the shape starts
        """
        slicing_indices = face_indices + [len(wound_faces)]
        return [
            wound_faces[slicing_indices[i] : slicing_indices[i + 1]]
            for i in range(len(face_indices))
        ]

    @staticmethod
    def unmap_pixel_ids(detector_id_mapping: List[List[int]], faces: int):
        """
        Returns a list of detector id's for faces in a components PixelMapping

        :param detector_id_mapping: A list of two-item lists. Each sublist contains a face ID followed by the face's
        detector ID. Corresponds to the detector_faces dataset of the NXoff_geometry class.
        :param faces: The total number of faces that should be mapped
        :return: a PixelMapping instance
        """
        pixel_ids = {}
        for mapping in detector_id_mapping:
            pixel_ids[mapping[0]] = mapping[1]
        return PixelMapping(
            pixel_ids=[
                pixel_ids[face_id] if face_id in pixel_ids else None
                for face_id in range(faces)
            ]
        )

    @staticmethod
    def build_pixel_grid(
        x_offsets: List[List[int]],
        y_offsets: List[List[int]],
        z_offsets: List[List[int]],
        detector_ids: List[List[int]],
    ):
        # Lists of 'row' sublists of 'column' length

        # Each array must be the same shape
        assert len(x_offsets) == len(y_offsets) == len(z_offsets) == len(detector_ids)
        for row in x_offsets[1:]:
            assert len(row) == len(x_offsets[0])
        for row in y_offsets:
            assert len(row) == len(x_offsets[0])
        for row in z_offsets:
            assert len(row) == len(x_offsets[0])
        for row in detector_ids:
            assert len(row) == len(x_offsets[0])

        rows = len(x_offsets)
        columns = len(x_offsets[0])

        if rows > 1:
            row_height = y_offsets[1][0] - y_offsets[0][0]
        else:
            row_height = 1

        if columns > 1:
            column_width = x_offsets[0][1] - x_offsets[0][0]
        else:
            column_width = 1

        corner_ids = {
            detector_ids[0][0]: Corner.BOTTOM_LEFT,
            detector_ids[0][columns - 1]: Corner.BOTTOM_RIGHT,
            detector_ids[rows - 1][0]: Corner.TOP_LEFT,
            detector_ids[rows - 1][columns - 1]: Corner.TOP_RIGHT,
        }
        first_id = min(corner_ids.keys())
        initial_count_corner = corner_ids[first_id]

        if rows > 1 and columns > 1:
            column_neighbour_ids = {
                Corner.BOTTOM_LEFT: detector_ids[1][0],
                Corner.BOTTOM_RIGHT: detector_ids[1][columns - 1],
                Corner.TOP_LEFT: detector_ids[rows - 2][0],
                Corner.TOP_RIGHT: detector_ids[rows - 2][columns - 1],
            }
            column_neighbour_id = column_neighbour_ids[initial_count_corner]
            if column_neighbour_id == first_id + 1:
                count_direction = CountDirection.COLUMN
            else:
                count_direction = CountDirection.ROW
        else:
            count_direction = CountDirection.ROW

        return PixelGrid(
            rows=rows,
            columns=columns,
            row_height=row_height,
            col_width=column_width,
            first_id=first_id,
            count_direction=count_direction,
            initial_count_corner=initial_count_corner,
        )

    @staticmethod
    def extract_dependency_names(dependency_path: str):
        """Takes the path to a nexus transform, and returns the name of the component and transform from it"""
        if dependency_path == ".":
            return None, None

        parts = dependency_path.split("/")
        return parts[-3], parts[-1]