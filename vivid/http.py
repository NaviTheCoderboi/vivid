"""
### vivid.http

A toy webframework made by me for learning purpose
"""
from collections.abc import Callable
from pathlib import Path
import typing as t
import uvicorn
from importlib import util
import jinja2
from vivid.utils.common import send_response, check_if_accepts_arg
import mimetypes
from types import ModuleType
from vivid import logger

__all__: tuple[str, ...] = ("Http",)


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
    logger.info(f"Loading {path.__str__()} (module)...")
    spec = util.spec_from_file_location(path.name, path)
    if spec and spec.loader:
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    else:
        return None


class Http:
    """
    Http class to create a vivid app

    Arguments
    ---------
    pages: dict[str, Path]
        Dictionary of routes and their corresponding pages
    server: dict[str, Path]
        Dictionary of routes and their corresponding server files
    static: dict[str, Path]
        Dictionary of routes and their corresponding static files
    scripts: dict[str, Path]
        Dictionary of routes and their corresponding scripts
    styles: dict[str, Path]
        Dictionary of routes and their corresponding styles

    Attributes
    ----------
    pages: dict[str, Path]
        Dictionary of routes and their corresponding pages
    server: dict[str, Path]
        Dictionary of routes and their corresponding server files
    static: dict[str, Path]
        Dictionary of routes and their corresponding static files
    scripts: dict[str, Path]
        Dictionary of routes and their corresponding scripts
    styles: dict[str, Path]
        Dictionary of routes and their corresponding styles
    """

    def __init__(
        self,
        pages: dict[str, Path],
        server: dict[str, Path],
        static: dict[str, Path],
        scripts: dict[str, Path],
        styles: dict[str, Path],
    ) -> None:
        self.pages = pages
        self.server = server
        self.static = static
        self.scripts = scripts
        self.styles = styles

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        """
        The main function of the app

        Arguments
        ---------
        scope: dict
            The scope of the request
        receive: collections.abc.Callable
            The receive function
        send: collections.abc.Callable
            The send function

        Returns
        -------
        None

        Raises
        ------
        Exception
            If an error occurs

        Notes
        -----
        This function is called by uvicorn
        """
        assert scope["type"] == "http"
        route: str = scope["path"]
        try:
            if route.startswith("/static"):
                body = self.serve_static(route)
                if body:
                    await send_response(
                        200,
                        body[0],
                        [[b"content-type", body[1].encode() if body else b"text/html"]],
                        send,
                    )
                else:
                    await self.render_not_found(send)
            elif route == "/favicon.ico":
                favicon = self.serve_static("/static/favicon.ico")
                if favicon:
                    await send_response(
                        200,
                        favicon[0],
                        [
                            [
                                b"content-type",
                                favicon[1].encode() if favicon else b"text/html",
                            ]
                        ],
                        send,
                    )
                else:
                    await self.render_not_found(send)
            elif route.startswith("/scripts"):
                body = await self.serve_script(route)
                if body:
                    await send_response(
                        200, body, [[b"content-type", b"text/javascript"]], send
                    )
                else:
                    await self.render_not_found(send)
            elif route.startswith("/styles"):
                body = await self.serve_styles(route)
                if body:
                    await send_response(
                        200, body, [[b"content-type", b"text/css"]], send
                    )
                else:
                    await self.render_not_found(send)
            else:
                body = self.return_template(self.pages[route])
                status = 200
                headers = [[b"content-type", b"text/html"]]
                if self.server.get(route):
                    mod = await self.load_server(self.server[route])
                    if mod:
                        data = await self.get_load_data(mod, await receive())
                        if data and body:
                            body = self.render_template(body, data.body)
                            if isinstance(body, Exception):
                                await self.render_error(send)
                                raise body
                            status = data.status
                            headers: list[list[str | bytes]] = data.headers
                        else:
                            await self.render_error(send)
                    else:
                        await self.render_error(send)
                if body:
                    await send_response(status, body, headers, send)
                else:
                    await self.render_not_found(send)
        except Exception as e:
            await self.render_error(send)
            raise e

    async def run(self) -> None:
        """
        Run the app

        Arguments
        ---------
        None

        Returns
        -------
        None
        """
        config = uvicorn.Config(self, host="localhost", port=8000, reload=True)
        server = uvicorn.Server(config)
        await server.serve()

    def return_template(self, template: Path) -> str | None:
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

    async def load_server(self, page: Path) -> ModuleType | None:
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
        logger.info("Loading server...")
        mod = load_mod(page)
        if mod:
            return mod
        else:
            return None

    async def get_load_data(
        self, mod: ModuleType, receive: dict[str, t.Any]
    ) -> t.Any | None:
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

    def render_template(self, template: str, data: dict[str, t.Any]) -> str | Exception:
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

    def serve_static(
        self, route: str
    ) -> tuple[bytes, str] | tuple[bytes, t.Literal["text/plain"]] | None:
        """
        Serve the static files

        Arguments
        ---------
        route: str
            The route to the static file

        Returns
        -------
        bytes | None
            The static file or None
        """
        try:
            with open(self.static[route.replace("/static", "")], "rb") as file:
                mime_type, _ = mimetypes.guess_type(
                    self.static[route.replace("/static", "")]
                )
                if mime_type:
                    return file.read(), mime_type
                return file.read(), "text/plain"
        except (FileNotFoundError, KeyError):
            return None

    async def render_not_found(self, send: Callable) -> None:
        """
        Render the 404 page

        Arguments
        ---------
        send: collections.abc.Callable
            The send function

        Returns
        -------
        None
        """
        try:
            body = self.return_template(self.pages["/404"])
            await send_response(
                404,
                body if body else "404 Not Found",
                [[b"content-type", b"text/html"]],
                send,
            )
        except KeyError:
            await send_response(
                404, "404 Not Found", [[b"content-type", b"text/html"]], send
            )

    async def render_error(self, send: Callable) -> None:
        """
        Render the 500 page

        Arguments
        ---------
        send: collections.abc.Callable
            The send function

        Returns
        -------
        None
        """
        try:
            body = self.return_template(self.pages["/500"])
            await send_response(
                500,
                body if body else "500 Internal Server Error",
                [[b"content-type", b"text/html"]],
                send,
            )
        except KeyError:
            await send_response(
                500,
                "500 Internal Server Error",
                [[b"content-type", b"text/html"]],
                send,
            )

    async def serve_script(self, route: str) -> str | None:
        """
        Serve the scripts

        Arguments
        ---------
        route: str
            The route to the script

        Returns
        -------
        str | None
            The script or None
        """
        try:
            with open(self.scripts[route.replace("/scripts", "")], "r") as file:
                return file.read()
        except (FileNotFoundError, KeyError):
            return None

    async def serve_styles(self, route: str) -> str | None:
        """
        Serve the styles

        Arguments
        ---------
        route: str
            The route to the style

        Returns
        -------
        str | None
            The style or None
        """
        try:
            with open(self.styles[route.replace("/styles", "")], "r") as file:
                return file.read()
        except (FileNotFoundError, KeyError):
            return None
