# Using Redis Background Task Controller with Lock by Args

## Example

```python
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller.py!}
```

## Running

Running the server:

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

## Creating tasks

Creating the task three times, getting error just on same arguments:

```bash
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl.bash!}
```

```
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl.bash.output!}
```

## Quering

Quering the server for the tasks:

```bash
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl2.bash!}
```

```
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl2.bash.output!}
```

Wait the tasks to finish and get results:


```bash
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl3.bash!}
```

```
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl3.bash.output!}
```

## Creating another task

Now the task should be able to run again

```bash
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl4.bash!}
```

```
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl4.bash.output!}
```

## Quering

Quering the server for the task (You must replace the task_id with the server output):

```bash
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl5.bash!}
```

```
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl5.bash.output!}
```

Wait the task to finish and get results:


```bash
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl6.bash!}
```

```
{!./src/redis_background_task_lock_args_controller/redis_background_task_lock_args_controller_curl6.bash.output!}
```
