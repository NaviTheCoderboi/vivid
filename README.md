# Vivid

<p align="center">
    <img width="120" src="./assets/vivid-logo.png" alt="Library Logo">
</p>

<p align="center">
    <strong>Vivid</strong> &rightarrow; A toy web framework made by me for learning purpose.<br><br>
    <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
	<img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/NaviTheCoderboi/vivid.svg">
	<img alt="GitHub stars" src="https://img.shields.io/github/stars/NaviTheCoderboi/vivid.svg">
</p>

## Installation

To install **Vivid** library, open a command line then write things those are below

```sh
python -m pip install vivid
```

If the top command isn't working, try this one

```sh
python3 -m pip install vivid
```

## Start quickly by creating project

To create a **Vivid** project you need to open a command line and type below command

```
python -m vivid new project -p .
```

> [!NOTE]
> **-p** is shorthand for **--path**

## walkthrough

You can load data on server using this server, make a **.py** file named same as template file in _/server_ directory.
you need to export a load function which returns a response, below is given an example **load** function

for example **index.py**

```python
from vivid.router import Response

async def load():
    return Response(200,[], { "name": "John" })
```

> [!NOTE]
> You have to use jinja3.x syntax for templating, Here's [jinja docs](https://jinja.palletsprojects.com/en/3.0.x/templates/) for more information.

### Example template

Here is an example template **index.html**

```html
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
```

## contributing

Everyone is free to fork and contribute to this project, hope this framework becomes a success!

**Made with ♥ by [NaviTheCoderboi](https://github.com/NaviTheCoderboi)**
