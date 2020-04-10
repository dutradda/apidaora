# Tutorial - Using Middlewares

## Example

```python
{!./src/tutorial/tutorial_11_middlewares.py!}
```

## Running 

Running the server:

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

## Quering the Post Routing Middleware

Quering the server:

```bash
{!./src/tutorial/tutorial_11_middlewares_curl.bash!}
```

```
{!./src/tutorial/tutorial_11_middlewares_curl.bash.output!}
```

## Quering the Pre Executition Middleware

```bash
{!./src/tutorial/tutorial_11_middlewares_curl2.bash!}
```

```
{!./src/tutorial/tutorial_11_middlewares_curl2.bash.output!}
```

## Quering the Post Executition Middleware

```bash
{!./src/tutorial/tutorial_11_middlewares_curl3.bash!}
```

```
{!./src/tutorial/tutorial_11_middlewares_curl3.bash.output!}
```
