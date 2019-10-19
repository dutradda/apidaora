# Tutorial - Using Async Background Task Controller

## Example

```python
{!./src/tutorial/tutorial_12_async_background_task_controller.py!}
```

Running the server (needs uvicorn [installed](https://www.uvicorn.org)):

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

Creating the task (needs curl [installed](https://curl.haxx.se/docs/install.html)):

```bash
{!./src/tutorial/tutorial_12_async_background_task_controller_curl.bash!}
```

```
{!./src/tutorial/tutorial_12_async_background_task_controller_curl.bash.output!}
```

Quering the server for the task:

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
