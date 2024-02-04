import shutil
import typing as t
from pathlib import Path
from types import ModuleType

import jinja2

from vivid.utils.common import check_if_accepts_arg, load_mod

__all__: tuple[str, ...] = (
    "return_template",
    "render_template",
    "copy_static_files_to",
    "load_server",
    "get_load_data",
    "get_static_load_data",
)


def return_template(template: Path) -> str | None:
    """
    Return the template

    Arguments
    ---------
    template: Path
        The path to the template

    Returns
    -------
    str | None
        The template or None
    """
    try:
        with open(template, "r") as file:
            return file.read()
    except FileNotFoundError:
        return None


def render_template(template: str, data: dict[str, t.Any]) -> str | Exception:
    """
    Render the template

    Arguments
    ---------
    template: str
        The template
    data: dict[str, typing.Any]
        The data to render the template

    Returns
    -------
    str | Exception
        The rendered template or an exception
    """
    try:
        env = jinja2.Template(template)
        return env.render(**data)
    except Exception as e:
        return e


def copy_static_files_to(path: Path, dest: Path) -> None:
    """
    Copy the static files to the destination

    Arguments
    ---------
    path: Path
        The path to the static files
    dest: Path
        The destination to copy the files to

    Returns
    -------
    None
    """
    if path.exists() and path.is_dir():
        shutil.copytree(path, dest, dirs_exist_ok=True)
        return


async def load_server(page: Path) -> ModuleType | None:
    """
    Load the server file

    Arguments
    ---------
    page: Path
        The path to the server file

    Returns
    -------
    ModuleType | None
        The loaded module or None
    """
    mod = load_mod(page)
    if mod:
        return mod
    else:
        return None


async def get_load_data(mod: ModuleType, receive: dict[str, t.Any]) -> t.Any | None:
    """
    Get the data from the load function

    Arguments
    ---------
    mod: ModuleType
        The loaded module

    Returns
    -------
    typing.Any
        The data from the load function
    """
    if hasattr(mod, "load"):
        if check_if_accepts_arg(mod.load, "receive"):
            try:
                return await mod.load(receive=receive)
            except TypeError:
                return mod.load(receive=receive)
        else:
            try:
                return await mod.load()
            except TypeError:
                return mod.load()
    else:
        return None


async def get_static_load_data(mod: ModuleType) -> t.Any | None:
    """
    Get the data from the load function

    Arguments
    ---------
    mod: ModuleType
        The loaded module

    Returns
    -------
    typing.Any
        The data from the load function
    """
    if hasattr(mod, "load"):
        try:
            return await mod.load()
        except TypeError:
            return mod.load()
    else:
        return None
