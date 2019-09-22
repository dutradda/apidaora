# apidaora

<p align="center" style="margin: 3em">
  <a href="https://github.com/dutradda/apidaora">
    <img src="https://dutradda.github.io/apidaora/apidaora.svg" alt="apidaora" width="300"/>
  </a>
</p>

<p align="center">
    <em>OpenAPI / HTTP / REST API using <b>dataclasses</b> and <b>TypedDict</b> annotation for python</b></em>
</p>

---

**Documentation**: <a href="https://dutradda.github.io/apidaora" target="_blank">https://dutradda.github.io/apidaora</a>

**Source Code**: <a href="https://github.com/dutradda/apidaora" target="_blank">https://github.com/dutradda/apidaora</a>

---


## Key Features

- Declare request objects as @jsondaora (can be TypedDict or @dataclass)
- Declare response objects as @jsondaora (can be TypedDict or @dataclass)


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
{!./src/index/index_02_openapi.py!}
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
{!./src/index/index_02_openapi_curl.bash!}
```

```
{!./src/index/index_02_openapi_curl.bash.output!}
```


## Example for more request/response details

```python
{!./src/index/index_03_openapi_more.py!}
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
{!./src/index/index_03_openapi_more_curl.bash!}
```

```
{!./src/index/index_03_openapi_more_curl.bash.output!}
```
