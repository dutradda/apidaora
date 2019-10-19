#!/bin/bash

echo -e '\n---------------------------------------'
echo -e 'Running examples outputs assertion...\n'

source ${VIRTUAL_ENV}/bin/activate

test_path=$(dirname ${BASH_SOURCE[0]})
test_regex="s%${test_path}/[^/]+/(.*)\.py%\1%g"
test_files="$(find ${test_path}/**/*.py)"

PYTHONPATH=${test_path}:${PYTHONPATH}

for filepath in ${test_files}; do
    filename=$(echo ${filepath} | sed -r -e ${test_regex})
    test_dir=$(dirname ${filepath})
    curl_file=${test_dir}/${filename}_curl.bash 
    output_tmpfile=/tmp/${filename}.output
    output_file=${curl_file}.output
    checksum_file=/tmp/${filename}.checksum
    curl_file2=${test_dir}/${filename}_curl2.bash 
    tmp_curl_file2=/tmp/${filename}_curl2.bash 
    output_file2=${curl_file2}.output
    output_tmpfile2=/tmp/${filename}2.output
    checksum_file2=/tmp/${filename}2.checksum
    curl_file3=${test_dir}/${filename}_curl3.bash 
    tmp_curl_file3=/tmp/${filename}_curl3.bash 
    output_file3=${curl_file3}.output
    output_tmpfile3=/tmp/${filename}3.output
    checksum_file3=/tmp/${filename}3.checksum
    date_regex="^date: .*"
    date_sub="date: Thu, 1st January 1970 00:00:00 GMT"
    task_time_regex='"(start|end)_time":"[0-9T:+-]+"'
    task_time_sub='"\1_time":"1970-01-01T00:00:00+00:00"'
    task_id_regex='.*"task_id":"([0-9a-z-]+)".*'
    task_id_sub='\1'
    uvicorn_output_file=/tmp/uvicorn-${filename}.output
    test_module=$(echo ${filepath} | tr '/' '.' | sed -r -e 's/\.py//g')

    echo Testing ${filename}..
    coverage run -p $(which uvicorn) ${test_module}:app >${uvicorn_output_file} 2>&1 &
    sleep 1

    bash ${curl_file} 2>/dev/null | \
        sed -r -e "s/${date_regex}/${date_sub}/g" \
            -e "s/${task_time_regex}/${task_time_sub}/g" \
            -e '$ s/(.*)/\1\n/g' > ${output_tmpfile}
    task_id=$(\
        cat ${output_tmpfile} | \
        grep -E "${task_id_regex}" | \
        sed -r -e "s/.*${task_id_regex}.*/${task_id_sub}/g" \
    )
    sed ${output_tmpfile} -i -r -e \
        "s/${task_id}/4ee301eb-6487-48a0-b6ed-e5f576accfc2/g" 2>/dev/null
    md5sum ${output_file} ${output_tmpfile} > ${checksum_file}

    if [ -f ${curl_file2} ]; then
        cp ${curl_file2} ${tmp_curl_file2}
        sed ${tmp_curl_file2} -i -r -e \
            "s/4ee301eb-6487-48a0-b6ed-e5f576accfc2/${task_id}/g" 2>/dev/null
        bash ${tmp_curl_file2} 2>/dev/null | \
            sed -r -e "s/${date_regex}/${date_sub}/g" \
                -e "s/${task_time_regex}/${task_time_sub}/g" \
                -e '$ s/(.*)/\1\n/g' > ${output_tmpfile2}
        sed ${output_tmpfile2} -i -r -e \
            "s/${task_id}/4ee301eb-6487-48a0-b6ed-e5f576accfc2/g" 2>/dev/null
        md5sum ${output_file2} ${output_tmpfile2} > ${checksum_file2}
    fi

    if [ -f ${curl_file3} ]; then
        cp ${curl_file3} ${tmp_curl_file3}
        sed ${tmp_curl_file3} -i -r -e \
            "s/4ee301eb-6487-48a0-b6ed-e5f576accfc2/${task_id}/g" 2>/dev/null
        bash ${tmp_curl_file3} 2>/dev/null | \
            sed -r -e "s/${date_regex}/${date_sub}/g" \
                -e "s/${task_time_regex}/${task_time_sub}/g" \
                -e '$ s/(.*)/\1\n/g' > ${output_tmpfile3}
        sed ${output_tmpfile3} -i -r -e \
            "s/${task_id}/4ee301eb-6487-48a0-b6ed-e5f576accfc2/g" 2>/dev/null
        md5sum ${output_file3} ${output_tmpfile3} > ${checksum_file3}
    fi

    ps ax | (ps ax | awk "/uvicorn ${test_module}:app/ {print \$1}" | xargs kill -SIGTERM 2>/dev/null)

    output=$(sed -r -e 's/(.*) .*/\1/g' ${checksum_file} | uniq | wc -l)

    if ! [ ${output} -eq 1 ]; then
        echo -e '\n\n\e[91mOutput assertion error!\e[0m\n\n'
        diff -u ${output_file} ${output_tmpfile}
        echo -e "\nuvicorn output: ${uvicorn_output_file}\n"
        cat ${uvicorn_output_file}
        exit 1
    fi

    if [ -f ${curl_file2} ]; then
        output2=$(sed -r -e 's/(.*) .*/\1/g' ${checksum_file2} | uniq | wc -l)

        if ! [ ${output2} -eq 1 ]; then
            echo -e '\n\n\e[91mOutput assertion error!\e[0m\n\n'
            diff -u ${output_file2} ${output_tmpfile2}
            echo -e "\nuvicorn output: ${uvicorn_output_file}\n"
            cat ${uvicorn_output_file}
            exit 1
        fi
    fi

    if [ -f ${curl_file3} ]; then
        output3=$(sed -r -e 's/(.*) .*/\1/g' ${checksum_file3} | uniq | wc -l)

        if ! [ ${output3} -eq 1 ]; then
            echo -e '\n\n\e[91mOutput assertion error!\e[0m\n\n'
            diff -u ${output_file3} ${output_tmpfile3}
            echo -e "\nuvicorn output: ${uvicorn_output_file}\n"
            cat ${uvicorn_output_file}
            exit 1
        fi
    fi

    echo OK
done

echo 'Docs examples outputs assertion passed!'
echo -e '---------------------------------------\n'
