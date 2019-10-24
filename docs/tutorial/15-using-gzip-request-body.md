# Tutorial - Using the gzip request body 

## Example

```python
{!./src/tutorial/tutorial_15_gzip_request_body.py!}
```

## Running

Running the server:

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

## Posting gzip file

Posting the file to the api (needs gzip [installed](https://www.gzip.org)):

```bash
{!./src/tutorial/tutorial_15_gzip_request_body_curl.bash!}
```

```
{!./src/tutorial/tutorial_15_gzip_request_body_curl.bash.output!}
```
