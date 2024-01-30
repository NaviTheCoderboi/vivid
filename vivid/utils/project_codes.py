__all__: tuple[str, ...] = ("index_html", "not_found", "index_css", "index_js", "index_py", "app_py", "get_ico")

index_html = """
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0" />
		<title>Document</title>
		<link rel="stylesheet" href="../styles/index.css" />
	</head>
	<body>
		<h1>Hello {{ name }}</h1>
		<script src="../scripts/index.js"></script>
	</body>
</html>
""".removeprefix("\n").removesuffix("\n")

not_found = """
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0" />
		<title>Document</title>
	</head>
	<body>
		404 Not Found (custom)
	</body>
</html>
""".removeprefix("\n").removesuffix("\n")

index_css = """
body {
    background-color: #000;
    color: #fff;
}

h1 {
    margin: 20px;
    background-color: blue;
}
""".removeprefix("\n").removesuffix("\n")

index_js = """
console.log("Hello World");
alert("Hello World");
""".removeprefix("\n").removesuffix("\n")

index_py = """
from vivid.router import Response

async def load():
    return Response(200,[], { "name": "..." })
""".removeprefix("\n").removesuffix("\n")

app_py = """
from vivid.router import App
from pathlib import Path

app = App(
    pages=Path(__file__).parent / "pages",
    server=Path(__file__).parent / "server",
    static=Path(__file__).parent / "static",
    scripts=Path(__file__).parent / "scripts",
    styles=Path(__file__).parent / "styles"
)
app.init()
app.run()
""".removeprefix("\n").removesuffix("\n")

def get_ico(path):
    from urllib.request import urlopen, Request

    url = "https://images.pexels.com/photos/1008737/pexels-photo-1008737.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url=url, headers=headers)
    data = urlopen(req).read()
    with open(path, "wb") as f:
        f.write(data)