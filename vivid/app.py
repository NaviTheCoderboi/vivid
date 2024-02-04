import asyncio
import typing as t
from dataclasses import dataclass
from pathlib import Path

from rich import print

from vivid.http import SSG, SSR

__all__: tuple[str, ...] = ("App", "Response")


class App:
    """
    App class to create a vivid app

    Arguments
    ---------
    pages: Path | str
        Path to pages directory
    server: Path | str
        Path to server directory
    static: Path | str
        Path to static directory
    scripts: Path | str
        Path to scripts directory
    styles: Path | str
        Path to styles directory
    type: typing.Literal["ssr"] | typing.Literal["ssg"]
        Type of the app

    Attributes
    ----------
    pages: Path
        Path to pages directory
    server: Path
        Path to server directory
    static: Path
        Path to static directory
    scripts: Path
        Path to scripts directory
    styles: Path
        Path to styles directory
    type: typing.Literal["ssr"] | typing.Literal["ssg"]
        Type of the app
    http: SSR | SSG | None
        HTTP instance of the app
    """

    def __init__(
        self,
        pages: Path | str,
        server: Path | str,
        static: Path | str,
        scripts: Path | str,
        styles: Path | str,
        type: t.Literal["ssr"] | t.Literal["ssg"] = "ssr",
    ) -> None:
        self.pages = Path(pages) if isinstance(pages, str) else pages
        self.server = Path(server) if isinstance(server, str) else server
        self.static = Path(static) if isinstance(static, str) else static
        self.scripts = Path(scripts) if isinstance(scripts, str) else scripts
        self.styles = Path(styles) if isinstance(styles, str) else styles
        self.type = type
        self.http: SSR | SSG | None = None

    def init(self) -> None:
        """
        Initialize the app by creating an SSR instance or an SSG instance

        Arguments
        ---------
        None

        Returns
        -------
        None
        """
        if self.type == "ssr":
            pages = {}
            for page in self.pages.rglob("*.html"):
                if "index.html" in str(page.name):
                    pages["/"] = page
                else:
                    pages["/" + str(page.relative_to(self.pages).as_posix()).replace(".html", "")] = page
            server = {}
            for file in self.server.rglob("*.py"):
                if "index.py" in str(file.name):
                    server["/"] = file
                else:
                    server["/" + str(file.relative_to(self.server).as_posix()).replace(".py", "")] = file
            static = {}
            for file in self.static.rglob("*"):
                if file.is_file():
                    static["/" + str(file.relative_to(self.static).as_posix())] = file
            scripts = {}
            for file in self.scripts.rglob("*.js"):
                if file.is_file():
                    scripts["/" + str(file.relative_to(self.scripts).as_posix())] = file
            styles = {}
            for file in self.styles.rglob("*.css"):
                if file.is_file():
                    styles["/" + str(file.relative_to(self.styles).as_posix())] = file
            self.http = SSR(
                pages=pages,
                server=server,
                static=static,
                scripts=scripts,
                styles=styles,
            )
        elif self.type == "ssg":
            pages = {}
            for page in self.pages.rglob("*.html"):
                if "index.html" in str(page.name):
                    pages["/"] = page
                else:
                    pages["/" + str(page.relative_to(self.pages).as_posix()).replace(".html", "")] = page
            server = {}
            for file in self.server.rglob("*.py"):
                if "index.py" in str(file.name):
                    server["/"] = file
                else:
                    server["/" + str(file.relative_to(self.server).as_posix()).replace(".py", "")] = file
            self.http = SSG(
                pages=pages,
                static=self.static,
                scripts=self.scripts,
                styles=self.styles,
                server=server,
            )

    def run(
        self,
        host: str = "localhost",
        port: int = 8000,
        dev: bool = False,
        reload_dirs: list[Path] = [],
    ) -> None:
        """
        Run the app if it is an SSR instance

        Arguments
        ---------
        host: str
            Host of the server
        port: int
            Port of the server
        dev: bool
            Whether to run in development mode
        reload_dirs: list[Path]
            Directories to reload on change

        Returns
        -------
        None
        """
        if self.type == "ssr" and isinstance(self.http, SSR):
            asyncio.get_event_loop().run_until_complete(
                self.http.run(host=host, port=port, dev=dev, reload_dirs=reload_dirs)
            )
        else:
            print("[#F43F5E bold]❌ Run method is only available for SSR instances[/#F43F5E bold]")
            exit(0)

    def build(self, dest: Path) -> None:
        """
        Build the app if it is an SSG instance

        Arguments
        ---------
        dest: Path
            Destination to build the app

        Returns
        -------
        None
        """
        if self.type == "ssg" and isinstance(self.http, SSG):
            asyncio.get_event_loop().run_until_complete(self.http.build(dest=dest))
        else:
            print("[#F43F5E bold]❌ Run method is only available for SSG instances[/#F43F5E bold]")
            exit(0)


@dataclass()
class Response:
    """
    Response class to create a vivid response

    Arguments
    ---------
    status: int
        Status code of the response
    headers: list[list[str | bytes]]
        Headers of the response
    body: dict[str, typing.Any]
        Body of the response
    """

    status: int
    headers: list[list[str | bytes]]
    body: dict[str, t.Any]

    def to_dict(self) -> dict[str, t.Any]:
        """
        Convert the response to a dictionary

        Arguments
        ---------
        None

        Returns
        -------
        dict[str, typing.Any]
            Dictionary representation of the response
        """
        return {"status": self.status, "headers": self.headers, "body": self.body}
