import typing as t
from collections.abc import Callable
from importlib import util
from pathlib import Path
from types import ModuleType

from rich import print

__all__: tuple[str, ...] = (
    "send_response",
    "check_if_accepts_arg",
    "load_mod",
    "create_file_from_route",
    "vlog",
)


async def send_response(status: int, body: t.Any, headers: list[list[str | bytes]], send: Callable[..., t.Any]) -> None:
    """
    Send a response to the client

    Arguments
    ---------
    status: int
        The status code of the response
    body: typing.Any
        The body of the response
    headers: list[list[str | bytes]]
    send: typing.Callable[..., typing.Any]
        The send function from the ASGI server

    Returns
    -------
    None
    """
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send(
        {
            "type": "http.response.body",
            "body": body.encode("utf-8") if isinstance(body, str) else body,
        }
    )


def check_if_accepts_arg(func: Callable[..., t.Any], arg: str) -> bool:
    """
    Check if a function accepts an argument

    Arguments
    ---------
    func: typing.Callable[..., typing.Any]
        The function to check
    arg: str
        The argument to check for

    Returns
    -------
    bool
        Whether the function accepts the argument
    """
    return arg in func.__code__.co_varnames


def load_mod(path: Path) -> ModuleType | None:
    """
    Load a module from a path

    Arguments
    ---------
    path: Path
        Path to the module

    Returns
    -------
    ModuleType | None
        The loaded module or None
    """
    spec = util.spec_from_file_location(path.name, path)
    if spec and spec.loader:
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    else:
        return None


def create_file_from_route(route: str, template: str, dest: Path) -> None:
    """
    Create a file from a route

    Arguments
    ---------
    route: str
        The route of the file
    template: str
        The template of the file
    dest: Path
        The destination to create the file

    Returns
    -------
    None
    """
    parts = route.split("/")[1:]
    filename = "/".join(parts) + ".html"
    if route == "/":
        filename = "index.html"
    (dest / filename).parent.mkdir(parents=True, exist_ok=True)
    (dest / filename).touch(exist_ok=True)
    with open(dest / filename, "w") as f:
        f.write(template)


def vlog(type: t.Literal["fail"] | t.Literal["success"], scope: t.Any, code: int) -> None:
    """
    Log a request

    Arguments
    ---------
    type: typing.Literal["fail"] | typing.Literal["success"]
        The type of the log
    scope: typing.Any
        The scope of the request
    code: int
        The status code of the request

    Returns
    -------
    None
    """
    print(
        ("[#2DD4BF]" if type == "success" else "[#F43F5E]")
        + f"{'✅' if type == 'success' else '❌'} {scope['client'][0]}:{scope['client'][1]} code: {code} {scope['method']} {scope['path']}"
        + "[/#2DD4BF]"
        if type == "success"
        else "[/#F43F5E]"
    )
