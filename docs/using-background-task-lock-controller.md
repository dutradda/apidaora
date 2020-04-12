# Using Background Task Controller with Lock

## Example

```python
{!./src/background_task_lock_controller/background_task_lock_controller.py!}
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

Creating the task twice, getting error on second:

```bash
{!./src/background_task_lock_controller/background_task_lock_controller_curl.bash!}
```

```
{!./src/background_task_lock_controller/background_task_lock_controller_curl.bash.output!}
```

## Quering

Quering the server for the task (You must replace the task_id with the server output):

```bash
{!./src/background_task_lock_controller/background_task_lock_controller_curl2.bash!}
```

```
{!./src/background_task_lock_controller/background_task_lock_controller_curl2.bash.output!}
```

Wait the task to finish and get results:


```bash
{!./src/background_task_lock_controller/background_task_lock_controller_curl3.bash!}
```

```
{!./src/background_task_lock_controller/background_task_lock_controller_curl3.bash.output!}
```

## Creating another task

Now the task should be able to run again

```bash
{!./src/background_task_lock_controller/background_task_lock_controller_curl4.bash!}
```

```
{!./src/background_task_lock_controller/background_task_lock_controller_curl4.bash.output!}
```

## Quering

Quering the server for the task (You must replace the task_id with the server output):

```bash
{!./src/background_task_lock_controller/background_task_lock_controller_curl5.bash!}
```

```
{!./src/background_task_lock_controller/background_task_lock_controller_curl5.bash.output!}
```

Wait the task to finish and get results:


```bash
{!./src/background_task_lock_controller/background_task_lock_controller_curl6.bash!}
```

```
{!./src/background_task_lock_controller/background_task_lock_controller_curl6.bash.output!}
```
