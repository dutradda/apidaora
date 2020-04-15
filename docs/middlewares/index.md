# Using Middlewares

## Example

```python
{!./src/middlewares/middlewares.py!}
```

## Running 

Running the server:

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

## Quering the Pre Executition Middleware

```bash
{!./src/middlewares/middlewares_curl.bash!}
```

```
{!./src/middlewares/middlewares_curl.bash.output!}
```

## Quering the Post Executition Middleware

```bash
{!./src/middlewares/middlewares_curl2.bash!}
```

```
{!./src/middlewares/middlewares_curl2.bash.output!}
```
