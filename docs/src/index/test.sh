#!/bin/bash

echo -e '\n---------------------------------------'
echo -e 'Running examples outputs assertion...\n'

source ${VIRTUALENV}/bin/activate

test_path=$(dirname ${BASH_SOURCE[0]})
tests_regex="s%${test_path}/(.*)\.py%\1%g"
test_files="$(find ${test_path}/*.py | sed -r -e ${tests_regex})"
# test_files="$(find ${test_path}/index_0*_openapi*.py | sed -r -e ${tests_regex})"

PYTHONPATH=${test_path}:${PYTHONPATH}

for filename in ${test_files}; do
    curl_file=${test_path}/${filename}_curl.bash 
    output_file=${curl_file}.output 
    output_tmpfile=/tmp/${filename}.output
    checksum_file=/tmp/${filename}.checksum
    date_regex="^date: .*"
    date_sub="date: Thu, 1st January 1970 00:00:00 GMT"
    uvicorn_output_file=/tmp/uvicorn-${filename}.output

    echo Testing ${filename}..
    uvicorn ${filename}:app >${uvicorn_output_file} 2>&1 &
    sleep 1

    bash ${curl_file} 2>/dev/null | \
        sed -r -e "s/${date_regex}/${date_sub}/g" \
            -r -e '$ s/(.*)/\1\n/g' > ${output_tmpfile}
    md5sum ${output_file} ${output_tmpfile} > ${checksum_file}

    ps ax | (ps ax | awk "/uvicorn ${filename}:app/ {print \$1}" | xargs kill -SIGTERM 2>/dev/null)

    output=$(sed -r -e 's/(.*) .*/\1/g' ${checksum_file} | uniq | wc -l)

    if ! [ ${output} -eq 1 ]; then
        echo -e '\n\n\e[91mOutput assertion error!\e[0m\n\n'
        diff -u ${output_file} ${output_tmpfile}
        echo -e "\nuvicorn output: ${uvicorn_output_file}\n"
        cat ${uvicorn_output_file}
        exit 1
    fi

    # sleep 1
    echo OK
done

echo 'Docs examples outputs assertion passed!'
echo -e '---------------------------------------\n'
