from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.prompt import Prompt

from vivid import __version__
from vivid.utils.cli import fetch_template

__all__: tuple[str, ...] = ()

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
click.rich_click.ERRORS_SUGGESTION = "Try running the '--help' flag for more information."
click.rich_click.ERRORS_EPILOGUE = "To find out more, visit [link=https://navithecoderboi.github.io/vivid/]https://navithecoderboi.github.io/vivid/[/link]"


def options_selector_using(options: list[str], prompt: str, console: Console) -> str:
    formatted_options = "\n".join(
        [
            f"[bold #14B8A6]{index + 1}.[/bold #14B8A6] [#6EE7B7]{option}[/#6EE7B7]"
            for index, option in enumerate(options)
        ]
    )
    console.print(formatted_options)
    selected_option = Prompt.ask(prompt, choices=[str(i + 1) for i in range(len(options))])
    console.print(
        f"[bold #84CC16]You selected:[/bold #84CC16] [bold #14B8A6]{options[int(selected_option) - 1]}[/bold #14B8A6]"
    )
    return options[int(selected_option) - 1]


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """
    Vivid is a CLI tool to scaffold your vivid projects.
    """
    pass


@main.command()
@click.argument(
    "_path",
    required=True,
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
)
def init(_path: str | Path) -> None:
    """
    Initialize a new vivid project.

    _path: The path where the project should be initialized.
    """
    console = Console()
    path = Path(_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    template_options = ["SSR", "SSG"]
    selected_template = options_selector_using(
        template_options,
        "[bold #84CC16]Select a template to use:[/bold #84CC16]",
        console,
    )
    fetch_template("SSR" if selected_template == "SSR" else "SSG", path)
    console.print(
        f"[bold #84CC16]Template downloaded successfully at:[/bold #84CC16] [bold #14B8A6]{path}[/bold #14B8A6]"
    )


if __name__ == "__main__":
    main()
