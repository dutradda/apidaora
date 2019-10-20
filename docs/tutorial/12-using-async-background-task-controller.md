# Tutorial - Using Async Background Task Controller

## Example

```python
{!./src/tutorial/tutorial_12_async_background_task_controller.py!}
```

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
{!./src/tutorial/tutorial_12_async_background_task_controller_curl.bash!}
```

```
{!./src/tutorial/tutorial_12_async_background_task_controller_curl.bash.output!}
```

## Quering

Quering the server for the task (You must replace the task_id with the server output):

```bash
{!./src/tutorial/tutorial_12_async_background_task_controller_curl2.bash!}
```

```
{!./src/tutorial/tutorial_12_async_background_task_controller_curl2.bash.output!}
```

Wait the task to finish and get results:


```bash
{!./src/tutorial/tutorial_12_async_background_task_controller_curl3.bash!}
```

```
{!./src/tutorial/tutorial_12_async_background_task_controller_curl3.bash.output!}
```
