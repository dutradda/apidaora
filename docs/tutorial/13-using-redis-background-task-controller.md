# Tutorial - Using Background Task Controller with Redis Backend

## Example

```python
{!./src/tutorial/tutorial_13_redis_background_task_controller.py!}
```

## Running

You will need a redis server to run this example.

Running the server (needs uvicorn [installed](https://www.uvicorn.org)):

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

Creating the task (needs curl [installed](https://curl.haxx.se/docs/install.html)):

```bash
{!./src/tutorial/tutorial_13_redis_background_task_controller_curl.bash!}
```

```
{!./src/tutorial/tutorial_13_redis_background_task_controller_curl.bash.output!}
```

Quering the server for the task:

```bash
{!./src/tutorial/tutorial_13_redis_background_task_controller_curl2.bash!}
```

```
{!./src/tutorial/tutorial_13_redis_background_task_controller_curl2.bash.output!}
```

Wait the task to finish and get results:


```bash
{!./src/tutorial/tutorial_13_redis_background_task_controller_curl3.bash!}
```

```
{!./src/tutorial/tutorial_13_redis_background_task_controller_curl3.bash.output!}
```
