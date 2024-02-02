"""
## Vivid.main

A toy webframework made by me for learning purpose
"""
import click
from pathlib import Path
from vivid import __version__, logger
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

        logger.info("Creating project template...")
        create_project(path)
        logger.info("Project template created!")
    except Exception as e:
        logger.error(e)


@main.command()
def run():
    try:
        from vivid.app.app import app

        logger.info("Starting application...")
        app.run()
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
