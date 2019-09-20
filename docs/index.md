# apidaora

<p align="center" style="margin: 3em">
  <a href="https://github.com/dutradda/apidaora">
    <img src="https://dutradda.github.io/apidaora/apidaora.svg" alt="apidaora" width="300"/>
  </a>
</p>

<p align="center">
    <em>HTTP/REST API using <b>dataclasses</b> and <b>TypedDict</b> annotation for python</b></em>
</p>

---

**Documentation**: <a href="https://dutradda.github.io/apidaora" target="_blank">https://dutradda.github.io/apidaora</a>

**Source Code**: <a href="https://github.com/dutradda/apidaora" target="_blank">https://github.com/dutradda/apidaora</a>

---


## Key Features

- Declare request objects as @jsondaora (can be TypedDict or @dataclass):
    + `PathArgs` for values on path
    + `Query` for values on query string
    + `Headers` for values on headers
    + `Body` for values on body

- Declare response objects as @jsondaora (can be TypedDict or @dataclass):
    + `Headers` for values on headers
    + `Body` for values on body


## Requirements

 - Python 3.7+
 - [jsondaora](https://github.com/dutradda/jsondaora) for json validation/parsing
 - [orjson](https://github.com/ijl/orjson) for json/bytes serialization (jsondaora dependency)


## Instalation
```
$ pip install apidaora
```


## Basic example

```python
{!./src/index/index_00_basic.py!}
```

Running the server (needs uvicorn [installed](https://www.uvicorn.org)):

```bash
{!./src/index/index__server.bash!}
```

```
{!./src/index/index__server.bash.output!}
```

Quering the server (needs curl [installed](https://curl.haxx.se/docs/install.html)):

```bash
{!./src/index/index_00_basic_curl.bash!}
```

```
{!./src/index/index_00_basic_curl.bash.output!}
```


## Example for complete request/response

```python
{!./src/index/index_01_complete.py!}
```

Running the server:

```bash
{!./src/index/index__server.bash!}
```

```
{!./src/index/index__server.bash.output!}
```

Quering the server:

```bash
{!./src/index/index_01_complete_curl.bash!}
```

```
{!./src/index/index_01_complete_curl.bash.output!}
```
