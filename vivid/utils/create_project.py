from pathlib import Path
from vivid.utils.project_codes import index_html, index_css, index_js, index_py,not_found, app_py, get_ico

__all__: tuple[str, ...] = ("create_project",)

def setup_pages(pages: Path):
    (pages / "index.html").touch()
    with open(pages / "index.html", "w") as f:
        f.write(index_html)
    (pages / "404.html").touch()
    with open(pages / "404.html", "w") as f:
        f.write(not_found)

def setup_server(server: Path):
    (server / "index.py").touch()
    with open(server / "index.py", "w") as f:
        f.write(index_py)

def setup_static(static: Path):
    (static / "favicon.ico").touch()
    get_ico(static / "favicon.ico")

def setup_styles(styles: Path):
    (styles / "index.css").touch()
    with open(styles / "index.css", "w") as f:
        f.write(index_css)

def setup_scripts(scripts: Path):
    (scripts / "index.js").touch()
    with open(scripts / "index.js", "w") as f:
        f.write(index_js)

def setup_app(path: Path):
    (path / "app.py").touch()
    with open(path / "app.py", "w") as f:
        f.write(app_py)

def create_project(path: Path):
    if path.exists() and path.is_dir():
        if len([i for i in path.iterdir()]) == 0:
            (path / "pages").mkdir(parents=True, exist_ok=True)
            (path / "server").mkdir(parents=True, exist_ok=True)
            (path / "static").mkdir(parents=True, exist_ok=True)
            (path / "styles").mkdir(parents=True, exist_ok=True)
            (path / "scripts").mkdir(parents=True, exist_ok=True)

            pages = path / "pages"
            server = path / "server"
            static = path / "static"
            styles = path / "styles"
            scripts = path / "scripts"

            setup_pages(pages)
            setup_server(server)
            setup_static(static)
            setup_styles(styles)
            setup_scripts(scripts)
            setup_app(path)
            print("Project created successfully at {}".format(path))
        else:
            raise Exception("Directory is not empty")
    elif not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        create_project(path)