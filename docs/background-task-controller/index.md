# Using Background Task Controller

## Example

```python
{!./src/background_task_controller/background_task_controller.py!}
```

## Running

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
{!./src/background_task_controller/background_task_controller_curl.bash!}
```

```
{!./src/background_task_controller/background_task_controller_curl.bash.output!}
```

## Quering

Quering the server for the task (You must replace the task_id with the server output):

```bash
{!./src/background_task_controller/background_task_controller_curl2.bash!}
```

```
{!./src/background_task_controller/background_task_controller_curl2.bash.output!}
```

Wait the task to finish and get results:


```bash
{!./src/background_task_controller/background_task_controller_curl3.bash!}
```

```
{!./src/background_task_controller/background_task_controller_curl3.bash.output!}
```
