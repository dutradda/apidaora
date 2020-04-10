# Using ASGI module

## Example

```python
{!./src/asgi_module/asgi_module.py!}
```

## Running

Running the server:

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

## Quering

Quering the server:

```bash
{!./src/asgi_module/asgi_module_curl.bash!}
```

```
{!./src/asgi_module/asgi_module_curl.bash.output!}
```

