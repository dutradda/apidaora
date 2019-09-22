curl -i -X PUT localhost:8000/hello/Me?location=World \
    -H 'x-req-id: 1243567890' \
    -d '{"last_name":"My Self","age":32}'
