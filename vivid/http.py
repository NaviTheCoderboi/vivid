import mimetypes
import typing as t
from collections.abc import AsyncGenerator, Callable
from pathlib import Path

import uvicorn
from rich.console import Console

from vivid.utils.common import create_file_from_route, send_response, vlog
from vivid.utils.http import (
    copy_static_files_to,
    get_load_data,
    get_static_load_data,
    load_server,
    render_template,
    return_template,
)

__all__: tuple[str, ...] = ("SSR", "SSG")

console = Console()


class SSR:
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

    async def __call__(
        self, scope: dict[str, t.Any], receive: Callable[..., t.Any], send: Callable[..., t.Any]
    ) -> None:
        """
        The main function of the app

        Arguments
        ---------
        scope: dict[str, typing.Any]
            The scope of the request
        receive: collections.abc.Callable[..., t.Any]
            The receive function
        send: collections.abc.Callable[..., t.Any]
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
        console.print(
            f"[#0EA5E9]🔗 {scope['client'][0]}:{scope['client'][1]} {scope['method']} {scope['path']}[/#0EA5E9]",
        )
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
                    vlog("success", scope, 200)
                else:
                    await self.render_not_found(send)
                    vlog("fail", scope, 404)
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
                    vlog("success", scope, 200)
                else:
                    await self.render_not_found(send)
                    vlog("fail", scope, 404)
            elif route.startswith("/scripts"):
                body = await self.serve_script(route)  # type: ignore[assignment]
                if body:
                    await send_response(200, body, [[b"content-type", b"text/javascript"]], send)
                    vlog("success", scope, 200)
                else:
                    await self.render_not_found(send)
                    vlog("fail", scope, 404)
            elif route.startswith("/styles"):
                body = await self.serve_styles(route)  # type: ignore[assignment]
                if body:
                    await send_response(200, body, [[b"content-type", b"text/css"]], send)
                    vlog("success", scope, 200)
                else:
                    await self.render_not_found(send)
                    vlog("fail", scope, 404)
            else:
                try:
                    body = return_template(self.pages[route])  # type: ignore[assignment]
                    status = 200
                    headers: list[list[str | bytes]] = [[b"content-type", b"text/html"]]
                    if self.server.get(route):
                        mod = await load_server(self.server[route])
                        if mod:
                            data = await get_load_data(mod, await receive())
                            if data and body and isinstance(body, str):
                                body = render_template(body, data.body)
                                if isinstance(body, Exception):
                                    await self.render_error(send)
                                    raise body
                                status = data.status
                                headers: list[list[str | bytes]] = data.headers  # type: ignore[no-redef]
                            else:
                                await self.render_error(send)
                                vlog("fail", scope, 500)
                        else:
                            await self.render_error(send)
                            vlog("fail", scope, 500)
                    if body:
                        await send_response(status, body, headers, send)
                        vlog("success", scope, status)
                    else:
                        await self.render_not_found(send)
                        vlog("fail", scope, 404)
                except KeyError:
                    await self.render_not_found(send)
                    vlog("fail", scope, 404)
        except Exception:
            await self.render_error(send)
            vlog("fail", scope, 500)
            console.print_exception()

    async def run(
        self,
        host: str = "localhost",
        port: int = 8000,
        dev: bool = False,
        reload_dirs: list[Path] = [],
    ) -> None:
        """
        Run the app

        Arguments
        ---------
        host: str
            The host of the app
        port: int
            The port of the app
        dev: bool
            Whether to run in development mode
        reload_dirs: list[Path]
            The directories to reload

        Returns
        -------
        None
        """
        config = uvicorn.Config(
            self,
            host=host,
            port=port,
            reload=dev,
            log_level="critical",
            reload_dirs=[path.as_posix() for path in reload_dirs],
        )
        server = uvicorn.Server(config)
        try:
            console.print(
                f"[#8B5CF6 bold]✅ Server running at http://{host}:{port}[/#8B5CF6 bold]",
                (f"[#D97706 bold]🚀 dev mode: {dev}[/#D97706 bold]\n"),
            )
            await server.serve()
        except KeyboardInterrupt:
            console.print("[#8B5CF6 bold]\n🛑 Server stopped[/#8B5CF6 bold]\n")
        except Exception as e:
            console.print(f"[#FF0000 bold]🚨 {e}[/#FF0000 bold]\n")

    def serve_static(self, route: str) -> tuple[bytes, str] | tuple[bytes, t.Literal["text/plain"]] | None:
        """
        Serve the static files

        Arguments
        ---------
        route: str
            The route to the static file

        Returns
        -------
        tuple[bytes, str] | tuple[bytes, t.Literal["text/plain"]] | None
            The static file or None
        """
        try:
            with open(self.static[route.replace("/static", "")], "rb") as file:
                mime_type, _ = mimetypes.guess_type(self.static[route.replace("/static", "")])
                if mime_type:
                    return file.read(), mime_type
                return file.read(), "text/plain"
        except (FileNotFoundError, KeyError):
            return None

    async def render_not_found(self, send: Callable[..., t.Any]) -> None:
        """
        Render the 404 page

        Arguments
        ---------
        send: collections.abc.Callable[..., t.Any]
            The send function

        Returns
        -------
        None
        """
        try:
            body = return_template(self.pages["/404"])
            await send_response(
                404,
                body if body else "404 Not Found",
                [[b"content-type", b"text/html"]],
                send,
            )
        except KeyError:
            await send_response(404, "404 Not Found", [[b"content-type", b"text/html"]], send)

    async def render_error(self, send: Callable[..., t.Any]) -> None:
        """
        Render the 500 page

        Arguments
        ---------
        send: collections.abc.Callable[..., t.Any]
            The send function

        Returns
        -------
        None
        """
        try:
            body = return_template(self.pages.get("/500") or self.pages["/500"])
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


class SSG:
    """
    SSG class to create a static site generator

    Arguments
    ---------
    pages: dict[str, Path]
        Dictionary of routes and their corresponding pages
    static: Path
        The static directory
    scripts: Path
        The scripts directory
    styles: Path
        The styles directory
    server: dict[str, Path]
        Dictionary of routes and their corresponding server files

    Attributes
    ----------
    pages: dict[str, Path]
        Dictionary of routes and their corresponding pages
    static: Path
        The static directory
    scripts: Path
        The scripts directory
    styles: Path
        The styles directory
    server: dict[str, Path]
        Dictionary of routes and their corresponding server files
    """

    def __init__(
        self,
        pages: dict[str, Path],
        static: Path,
        scripts: Path,
        styles: Path,
        server: dict[str, Path],
    ) -> None:
        self.pages = pages
        self.static = static
        self.scripts = scripts
        self.styles = styles
        self.server = server

    async def get_templates_with_data(
        self,
    ) -> AsyncGenerator[dict[str, tuple[Path, dict[str, t.Any] | None]], None]:
        """
        Get the templates with their corresponding data

        Arguments
        ---------
        None

        Yields
        ------
        dict[str, tuple[Path, dict[str, typing.Any] | None]]
            The templates with their corresponding data
        """
        for page in self.pages:
            if page == "/404" or page == "/500":
                yield {page: (self.pages[page], None)}
            else:
                if self.server.get(page):
                    mod = await load_server(self.server[page])
                    if mod:
                        data = await get_static_load_data(mod)
                        if data:
                            yield {page: (self.pages[page], data.body)}
                        else:
                            yield {page: (self.pages[page], None)}
                    else:
                        yield {page: (self.pages[page], None)}
                else:
                    yield {page: (self.pages[page], None)}

    async def build(self, dest: Path) -> None:
        """
        Build the static site

        Arguments
        ---------
        dest: Path
            The destination directory

        Returns
        -------
        None
        """
        console.print(f"[#8B5CF6 bold]🔨 Building to {dest.as_posix()}[/#8B5CF6 bold]\n")
        async for pageAndData in self.get_templates_with_data():
            for page, (template, data) in pageAndData.items():
                body = return_template(template)
                if body:
                    if data:
                        _body = render_template(body, data)
                        if isinstance(_body, Exception):
                            raise _body
                        try:
                            create_file_from_route(page, _body, dest)
                            console.print(f"[#0EA5E9]✅ {page} created[/#0EA5E9]")
                        except Exception:
                            console.print_exception()
                    else:
                        try:
                            console.print(f"[#0EA5E9]✅ {page} created[/#0EA5E9]")
                            create_file_from_route(page, body, dest)
                        except Exception:
                            console.print_exception()
        try:
            console.print("[#8B5CF6 bold]🔨 Copying static files[/#8B5CF6 bold]")
            copy_static_files_to(self.static, dest / "static")
        except Exception:
            console.print_exception()
        finally:
            console.print("[#0EA5E9 bold]✅ Copied static[/#0EA5E9 bold]")
        try:
            console.print("[#8B5CF6 bold]🔨 Copying scripts[/#8B5CF6 bold]")
            copy_static_files_to(self.scripts, dest / "scripts")
        except Exception:
            console.print_exception()
        finally:
            console.print("[#0EA5E9 bold]✅ Copied scripts[/#0EA5E9 bold]")
        try:
            console.print("[#8B5CF6 bold]🔨 Copying styles[/#8B5CF6 bold]")
            copy_static_files_to(self.styles, dest / "styles")
        except Exception:
            console.print_exception()
        finally:
            console.print("[#0EA5E9 bold]✅ Copied styles[/#0EA5E9 bold]")
        console.print("[#8B5CF6 bold]\n✅ Build complete\n[/#8B5CF6 bold]")
        console.print("[#FACC15 bold]⚠ Make sure to fix the srcs and hrefs of scripts and stlyes[/#FACC15 bold]")
