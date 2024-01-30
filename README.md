# Vivid

<p align="center">A toy webframework made by me for learning purpose.</p>
![](https://img.shields.io/pypi/v/vivid?style=flat-square)

## Installation

install the vivid library from pypi using pip

```sh
python -m pip install vivid
```

## Create project

create a vivid project using vivid cli
run the following command

```
python -m vivid new project -p .
```

**-p** is shorthand for **--path**

## walkthrough

you can load data on server using this server, make a **.py** file named same as template file in _/server_ directory.
you need to export a load function which returns a response, below is given an example **load** function

for example **index.py**

```python
from vivid.router import Response

async def load():
    return Response(200,[], { "name": "John" })
```

You need to use jinja3.x syntax for templating, visit [jinja docs](https://jinja.palletsprojects.com/en/3.0.x/templates/) for learning more

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
