# Using the gzip request body 

## Example

```python
{!./src/gzip_request_body/gzip_request_body.py!}
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
{!./src/gzip_request_body/gzip_request_body_curl.bash!}
```

```
{!./src/gzip_request_body/gzip_request_body_curl.bash.output!}
```
