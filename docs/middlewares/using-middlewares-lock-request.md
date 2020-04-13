# Using Lock Request Middleware

## Example

```python
{!./src/lock_request/lock_request.py!}
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
{!./src/lock_request/lock_request_curl.bash!}
```

```
{!./src/lock_request/lock_request_curl.bash.output!}
```
