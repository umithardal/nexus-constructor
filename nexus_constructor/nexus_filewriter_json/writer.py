import h5py

from nexus_constructor.instrument import Instrument
import numpy as np
import json
import uuid


def generate_json(data: Instrument, file):
    """
    Returns a formatted json string built from a given Instrument
    The json description can be used by the file writer (github.com/ess-dmsc/kafka-to-nexus) to create a NeXus file

    :param data: The full description of the beamline and data
    """

    streams = []
    links = []
    nexus_file_name = ""

    converter = NexusToDictConverter()
    tree = converter.convert(data.nexus, streams, links)
    write_command, stop_command = create_writer_commands(tree, nexus_file_name)
    object_to_json_file(write_command, file)


class NexusToDictConverter:
    """
    Class used to convert nexus format root to python dict
    """

    def __init__(self, truncate_large_datasets=False, large=10):
        """
        :param truncate_large_datasets: if True truncates datasets with any dimension larger than large
        :param large: dimensions larger than this are considered large
        """
        self._kafka_streams = dict()
        self._links = dict()
        self.truncate_large_datasets = truncate_large_datasets
        self.large = large

    def convert(self, nexus_root, streams, links):
        """
        Converts the given nexus_root to dict with correct replacement of
        the streams
        :param links:
        :param nexus_root
        :param streams:
        :return: dictionary
        """
        self._kafka_streams = streams
        self._links = links
        return {
            "children": [
                self._root_to_dict(entry) for _, entry in nexus_root.entries.items()
            ]
        }

    def _root_to_dict(self, root):
        if hasattr(root, "entries"):
            root_dict = self._handle_group(root)
        else:
            root_dict = self._handle_dataset(root)

        root_dict = self._handle_attributes(root, root_dict)
        return root_dict

    @staticmethod
    def truncate_if_large(size, data):
        for dim_number, dim_size in enumerate(size):
            if dim_size > 10:
                size[dim_number] = 10
        data.resize(size)

    def _get_data_and_type(self, root: h5py.Dataset):
        """
        get data type of dataset
        :param root: h5py dataset
        :return: the data in the dataset, the datatype and the size of the data in the dataset
        """
        size = 1
        data = root.value
        dtype = root.dtype
        if isinstance(data, np.ndarray):
            size = data.shape
            if self.truncate_large_datasets:
                self.truncate_if_large(size, data)
            data = data.tolist()
        if dtype.char == "S":
            if isinstance(data, list):
                data = [str_item.decode("utf-8") for str_item in data]
            else:
                data = data.decode("utf-8")
            dtype = "string"
        elif dtype is np.float64:
            dtype = "double"
        elif dtype is np.float:
            dtype = "float"
        return data, dtype, size

    def _handle_attributes(self, root, root_dict):
        if (
            root.nxclass
            and root.nxclass is not "NXfield"
            and root.nxclass is not "NXgroup"
        ):
            root_dict["attributes"] = [{"name": "NX_class", "values": root.nxclass}]
        if root.attrs:
            if "attributes" not in root_dict:
                root_dict["attributes"] = []
            root_dict["attributes"] = []
            for attr_name, attr in root.attrs.items():
                data, dtype, size = self._get_data_and_type(attr)
                new_attribute = {"name": attr_name, "values": data}
                if dtype != "object":
                    new_attribute["type"] = dtype
                root_dict["attributes"].append(new_attribute)
        return root_dict

    def _handle_group(self, root: h5py.Group):
        """
        Generate JSON dict for a h5py group.
        :param root: h5py group to generate dict from.
        :return: generated dict of group and children.
        """
        root_dict = {"type": "group", "name": root.nxname, "children": []}
        # Add the entries
        entries = root.entries
        if root.nxpath in self._kafka_streams:
            root_dict["children"].append(
                {"type": "stream", "stream": self._kafka_streams[root.nxpath]}
            )
        elif root.nxpath in self._links:
            root_dict["children"].append(
                {
                    "type": "link",
                    "name": self._links[root.nxpath]["name"],
                    "target": self._links[root.nxpath]["target"],
                }
            )
        elif entries:
            for entry in entries:
                child_dict = self._root_to_dict(entries[entry])
                root_dict["children"].append(child_dict)

        return root_dict

    def _handle_dataset(self, root: h5py.Dataset):
        """
        Generate JSON dict for a h5py dataset.
        :param root: h5py dataset to generate dict from.
        :return: generated dictionary of dataset values and attrs.
        """
        data, dataset_type, size = self._get_data_and_type(root)
        root_dict = {
            "type": "dataset",
            "name": root.nxname,
            "dataset": {"type": dataset_type},
            "values": data,
        }
        if size != 1:
            root_dict["dataset"]["size"] = size

        return root_dict


def object_to_json_file(tree_dict, file):
    """
    Create a JSON file describing the NeXus file
    WARNING, output files can easily be 10 times the size of input NeXus file

    :param tree_dict: Root node of the tree.
    :param file: File object to store the tree in.
    """

    json.dump(tree_dict, file, indent=2, sort_keys=False)


def create_writer_commands(
    nexus_structure,
    output_filename,
    broker="localhost:9092",
    job_id="",
    start_time=None,
    stop_time=None,
):
    """
    :param nexus_structure:
    :param output_filename:
    :param broker:
    :param job_id:
    :param start_time: ms from unix epoch
    :param stop_time: ms from unix epoch
    :return:
    """
    if not job_id:
        job_id = str(uuid.uuid1())

    write_cmd = {
        "cmd": "FileWriter_new",
        "broker": broker,
        "job_id": job_id,
        "file_attributes": {"file_name": output_filename},
        "nexus_structure": nexus_structure,
    }
    if start_time is not None:
        write_cmd["start_time"] = start_time

    stop_cmd = {"cmd": "FileWriter_stop", "job_id": job_id}
    if stop_time is not None:
        stop_cmd["stop_time"] = stop_time

    return write_cmd, stop_cmd
