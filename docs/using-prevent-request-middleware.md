# Using Prevent Request Middleware

## Example

```python
{!./src/prevent_request/prevent_request.py!}
```

## Running 

Running the server:

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

## Post a large json file several times

```bash
{!./src/prevent_request/prevent_request_curl.bash!}
```

```
{!./src/prevent_request/prevent_request_curl.bash.output!}
```
