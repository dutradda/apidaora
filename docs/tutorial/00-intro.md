# Tutorial - Introduction

## Getting Started

### Installs

```
$ pip install apidaora
```

### Starts coding

```python
{!./src/index/index_00_simple.py!}
```

Running the server (needs uvicorn [installed](https://www.uvicorn.org)):

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

Quering the server (needs curl [installed](https://curl.haxx.se/docs/install.html)):

```bash
{!./src/index/index_00_simple_curl.bash!}
```

```
{!./src/index/index_00_simple_curl.bash.output!}
```
