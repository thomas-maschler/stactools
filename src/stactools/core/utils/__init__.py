from typing import Callable, Optional, TypeVar

import fsspec

T = TypeVar('T')
U = TypeVar('U')


def map_opt(fn: Callable[[T], U], v: Optional[T]) -> Optional[U]:
    """Maps the value of an option to another value, returning
    None if the input option is None.
    """
    return v if v is None else fn(v)


def href_exists(href: str) -> bool:
    """Returns true if the asset exists.

    Uses fssepc and its `exists` method:
    https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.spec.AbstractFileSystem.exists.
    """
    fs, _, paths = fsspec.get_fs_token_paths(href)
    return paths and fs.exists(paths[0])
