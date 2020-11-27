## CHANGELOG

### 0.28.0 - 2020-11-27

 - Add css and javascript content types

### 0.27.2 - 2020-08-31

 - Fix background_task module

### 0.27.1 - 2020-07-29

 - Add logging messages for bad requests

### 0.27.0 - 2020-07-08

 - Improve responses

### 0.26.1 - 2020-05-08

 - Fix tests for new jsondaora version

### 0.26.0 - 2020-04-14

 - Improve background task controller to return 303 instead 400

 - Refactor the package to has a common request object

 - Change background task controller creation status code from 201 to 202

 - Fix background task controller finished task

### 0.25.0 - 2020-04-14

 - Refactor background task controller to build unique tasks ids when locking args

 - Fix task_id on background tasks controller when lock args is true

 - Fix RedisTasksRepository.get method

### 0.24.0 - 2020-04-13

 - Improve background task controller

### 0.23.0 - 2020-04-12

 - Create background tasks middlewares

### 0.22.1 - 2020-04-12

 - Fix factory when has middlewares and the controller has no inputs

### 0.22.0 - 2020-04-12

 - Improve router

### 0.21.0 - 2020-04-12

 - Create feature to pass kwargs through middlewares and controller

 - Improve post_execution middleware

 - Rename PreventRequestMiddleware to LockRequestMiddleware

### 0.20.0 - 2020-04-12

 - Add docs for background tasks with lock args and redis

 - Create the feature task background lock by args

 - Rename the feature background task single running to background task lock

### 0.19.0 - 2020-04-12

 - Fix middleware request parsing

 - Create single running feature for background tasks

### 0.18.0 - 2020-04-11

 - Create prevent request middleware

 - Fix merge of general middlewares and route middlewares

 - Improve Request class

### 0.17.2 - 2020-04-10

 - Fix asgi headers for h11 http parser

### 0.17.1 - 2020-04-10

 - Fix cors middleware

### 0.17.0 - 2020-04-10

 - Improve post routing middleware

### 0.16.1 - 2020-04-10

 - Change docs to dark theme

### 0.16.0 - 2020-04-10

 - Add class controllers support

### 0.15.1 - 2020-04-10

 - Improve docs

 - Fix make_not_found_response function

### [0.15.0 - 2020-04-10]

 - Create default options controller

 - Add middlewares support

### 0.14.1 - 2020-04-04

 - Fix controller_output serialization

### 0.14.0 - 2020-03-06

 - Add support for str bodies

### 0.13.0 - 2020-03-04

 - Create not_found and no_content responses types

 - Add deserialization on query args

 - Update devtools

### 0.12.0 - 2019-12-12

 - Add LRU cache for router to optimizing resolutions

### 0.11.4 - 2019-10-24

 - Fix background tasks redis

### 0.11.3 - 2019-10-24

 - Fix background tasks

### 0.11.2 - 2019-10-23

 - Improve mypy

### 0.11.1 - 2019-10-23

 - Add package typing

### 0.11.0 - 2019-10-22

 - Fix background task status code

 - Create core module interface

### 0.10.0 - 2019-10-20

 - Add gzip upload support

 - Create background tasks feature

### 0.9.0 - 2019-10-07

 - Improve response types

 - Fix headers response

### 0.8.0 - 2019-10-07

 - Fix headers response

### 0.7.0 - 2019-10-06

 - Improve devtools

 - Improve docs

 - Refactor the entirely api

### 0.6.0 - 2019-10-04

 - Add devtools submodule

 - Refactor path decorator

 - Improve examples to use async def

 - Update public interface

 - Improve docs


### 0.5.0 (2019-09-20)

 - Improves requests/responses objects


### 0.4.1 (2019-09-19)

 - Improve docs


### 0.4.0 (2019-09-19)

 - Rename typingjson project do jsondaora


### 0.3.0 (2019-09-19)

 - Add TypedDict support

 - Rename project


### 0.2.0 (2019-09-18)

 - Refactor app and router modules


### 0.1.2 (2019-09-18)

 - Improve docs


### 0.1.1 (2019-09-18)

 - Fix docs


### 0.1.0 (2019-09-18)

 - Add initial files
