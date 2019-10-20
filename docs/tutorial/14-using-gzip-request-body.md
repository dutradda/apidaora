# Tutorial - Using the gzip request body 

## Example

```python
{!./src/tutorial/tutorial_14_gzip_request_body.py!}
```

## Running

Running the server (needs uvicorn [installed](https://www.uvicorn.org)):

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

Posting the file to the api (needs gzip [installed](https://www.gzip.org)):

```bash
{!./src/tutorial/tutorial_14_gzip_request_body_curl.bash!}
```

```
{!./src/tutorial/tutorial_14_gzip_request_body_curl.bash.output!}
```
