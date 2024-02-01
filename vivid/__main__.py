import click
from pathlib import Path
from vivid import __version__
from vivid.utils.create_project import create_project

__all__: tuple[str, ...] = ()


@click.group()
@click.version_option(version=__version__)
def main():
    pass


@main.group()
def new():
    pass


@new.command()
@click.option(
    "--path",
    "-p",
    default="./",
    help="Path to create project",
    type=click.Path(exists=False),
)
def project(path: str | Path):
    try:
        if isinstance(path, str):
            path = Path(path).resolve()
        create_project(path)
    except Exception as e:
        print("Error: {}".format(e))


@main.command()
def run():
    try:
        from vivid.app.app import app

        app.run()
    except Exception as e:
        print("Error: {}".format(e))


if __name__ == "__main__":
    main()
