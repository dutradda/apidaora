# Using Background Task Controller with Redis Backend

## Example

```python
{!./src/redis_background_task_controller/redis_background_task_controller.py!}
```

## Running

You will need a redis server to run this example.

Running the server:

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

## Creating task

Creating the task:

```bash
{!./src/redis_background_task_controller/redis_background_task_controller_curl.bash!}
```

```
{!./src/redis_background_task_controller/redis_background_task_controller_curl.bash.output!}
```

## Quering

Quering the server for the task (You must replace the task_id with the server output):

```bash
{!./src/redis_background_task_controller/redis_background_task_controller_curl2.bash!}
```

```
{!./src/redis_background_task_controller/redis_background_task_controller_curl2.bash.output!}
```

Wait the task to finish and get results:


```bash
{!./src/redis_background_task_controller/redis_background_task_controller_curl3.bash!}
```

```
{!./src/redis_background_task_controller/redis_background_task_controller_curl3.bash.output!}
```
