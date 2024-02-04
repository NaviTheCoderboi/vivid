import typing as t
import urllib.request
import zipfile
from io import BytesIO
from pathlib import Path

from rich import print
from rich.progress import wrap_file

__all__: tuple[str, ...] = ("fetch_template",)


def fetch_template(type: t.Literal["SSR"] | t.Literal["SSG"], dest: Path) -> None:
    """
    Fetches the template from the vivid-templates repository.

    Arguments
    ---------
    type : Literal["SSR", "SSG"]
        The type of template to fetch.
    dest : Path
        The destination where the template should be extracted.

    Raises
    ------
    urllib.error.URLError
        If the URL is invalid.
    zipfile.BadZipFile
        If the zip file is corrupted.
    Exception
        If any other error occurs.
    """
    try:
        username = "navithecoderboi"
        repository = "vivid-templates"
        url = f"https://github.com/{username}/{repository}/archive/refs/heads/{type.lower()}.zip"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        with urllib.request.urlopen(req) as response:
            size = int(response.headers["Content-Length"])
            with wrap_file(
                response,
                size,
                description=f"[rgb(6,182,212)]Downloading {type} template...[rgb(6,182,212)]",
            ) as file:
                data = file.read()
                with zipfile.ZipFile(BytesIO(data)) as zip_ref:
                    zip_ref.extractall(dest)
    except Exception as e:
        print(f"[bold red]Error:[/bold red] {e}")
        print("[bold magenta italic]Try running the '--help' flag for more information.")
