# Tutorial - Using ASGI module

## Example

```python
{!./src/tutorial/tutorial_10_asgi_module.py!}
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
{!./src/tutorial/tutorial_10_asgi_module_curl.bash!}
```

```
{!./src/tutorial/tutorial_10_asgi_module_curl.bash.output!}
```

