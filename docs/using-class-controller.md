# Using Class Controller

## Example

```python
{!./src/class_controller/class_controller.py!}
```

## Running 

Running the server:

```bash
uvicorn myapp:app
```

```
{!./src/server.bash.output!}
```

## Quering the .get method

Quering the server:

```bash
{!./src/class_controller/class_controller_curl.bash!}
```

```
{!./src/class_controller/class_controller_curl.bash.output!}
```

## Quering the .post method

```bash
{!./src/class_controller/class_controller_curl2.bash!}
```

```
{!./src/class_controller/class_controller_curl2.bash.output!}
```

## Quering the duck type class with .get method 

```bash
{!./src/class_controller/class_controller_curl3.bash!}
```

```
{!./src/class_controller/class_controller_curl3.bash.output!}
```
