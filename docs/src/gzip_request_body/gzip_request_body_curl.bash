echo -n 'Hello World!' | gzip > hello.gz

curl -X POST -i localhost:8000/hello --upload-file hello.gz
