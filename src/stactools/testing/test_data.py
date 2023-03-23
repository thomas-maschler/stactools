import os
import shutil
from tempfile import TemporaryDirectory
from typing import Any, Dict
from zipfile import ZipFile

import fsspec
import requests

# TODO make external data a dataclass

# example external data:
# {
#     'AST_L1T_00305032000040446_20150409135350_78838.hdf': {
#         'url':
#         ('https://ai4epublictestdata.blob.core.windows.net/'
#          'stactools/aster/AST_L1T_00305032000040446_20150409135350_78838.zip'),
#         'compress':
#         'zip'
#     }
# }


class TestData:
    """A structure for getting paths to test data files, and fetching external
    data for local testing.

    Initialize this from, e.g., ``tests/__init__.py``:

    .. code-block:: python

        test_data = TestData(__file__)

    The external data dictionary should look something like this:

    .. code-block:: python

        {
            'AST_L1T_00305032000040446_20150409135350_78838.hdf': {
                'url':
                    ('https://ai4epublictestdata.blob.core.windows.net/'
                    'stactools/aster/AST_L1T_00305032000040446_20150409135350_78838.zip'),
                'compress': 'zip'
            }
        }

    Args:
        path (str): The path to the file at the root of the test data directory.
        external_data (dict[str, Any]):
            External data configurations. These dictionaries can be used to
            configure files that are fetched from remote locations and stored
            locally for testing.
    """

    __test__ = False

    def __init__(self, path: str, external_data: Dict[str, Any] = {}) -> None:
        self.path = path
        self.external_data = external_data

    def get_path(self, rel_path: str) -> str:
        """Returns an absolute path to a local test file.

        Args:
            rel_path (str):
                The relative path to the test data file. The path is
                assumed to be relative to the directory containing ``self.path``.

        Returns:
            str: An absolute path.
        """
        return os.path.abspath(os.path.join(os.path.dirname(self.path), rel_path))

    def get_external_data(self, rel_path: str) -> str:
        """Returns an absolute path to a local test file after downloading it
        from an external source.

        Args:
            rel_path (str): The key to the external data, as configured in class
                instantiation.

        Returns:
            str: The absolute path to the external data file.
        """
        path = self.get_path(os.path.join("data-files/external", rel_path))
        if not os.path.exists(path):
            entry = self.external_data.get(rel_path)
            if entry is None:
                raise Exception(
                    "Path {} does not exist and there is no entry "
                    "for external test data {}.".format(path, rel_path)
                )

            print("Downloading external test data {}...".format(rel_path))
            os.makedirs(os.path.dirname(path), exist_ok=True)

            s3_config = entry.get("s3")
            is_pc = entry.get("planetary_computer")  # True if from PC, needs signing
            if s3_config:
                try:
                    import s3fs
                except ImportError as e:
                    print(
                        "Trying to download external test data via s3, "
                        "but s3fs is not installed and the download requires "
                        "configuring the s3fs filesystem. Install stactools "
                        "with s3fs via `pip install stactools[s3]` and try again."
                    )
                    raise (e)
                s3 = s3fs.S3FileSystem(**s3_config)
                with s3.open(entry["url"]) as f:
                    data = f.read()
            elif is_pc:
                href = entry["url"]
                r = requests.get(
                    "https://planetarycomputer.microsoft.com/api/sas/v1/sign?"
                    f"href={href}"
                )
                r.raise_for_status()
                signed_href = r.json()["href"]

                with fsspec.open(signed_href) as f:
                    data = f.read()

            else:
                with fsspec.open(entry["url"]) as f:
                    data = f.read()

            if entry.get("compress") == "zip":
                with TemporaryDirectory() as tmp_dir:
                    tmp_path = os.path.join(tmp_dir, "file.zip")
                    with open(tmp_path, "wb") as f:
                        f.write(data)
                    z = ZipFile(tmp_path)
                    name = z.namelist()[0]
                    extracted_path = z.extract(name)
                    shutil.move(extracted_path, path)
            else:
                with open(path, "wb") as f:
                    f.write(data)

        return path
