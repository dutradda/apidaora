# Using Background Tasks Middleware

## Example

```python
{!./src/middlewares_background_task/middlewares_background_task.py!}
```

## Running 

Running the server:

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

## Quering the server

```bash
{!./src/middlewares_background_task/middlewares_background_task_curl.bash!}
```

```
{!./src/middlewares_background_task/middlewares_background_task_curl.bash.output!}
```
