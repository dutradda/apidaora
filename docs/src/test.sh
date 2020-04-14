#!/bin/bash

echo -e '\n---------------------------------------'
echo -e 'Running examples outputs assertion...\n'

source ${VIRTUAL_ENV}/bin/activate

test_path=$(dirname ${BASH_SOURCE[0]})
test_regex="s%${test_path}/[^/]+/(.*)\.py%\1%g"
if test -n "${1}"; then
    test_files="${test_path}/${1}/${1}.py"
else
    test_files="$(find ${test_path}/**/*.py | grep -v __init__)"
fi

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
    curl_file4=${test_dir}/${filename}_curl4.bash
    tmp_curl_file4=/tmp/${filename}_curl4.bash
    output_file4=${curl_file4}.output
    output_tmpfile4=/tmp/${filename}4.output
    checksum_file4=/tmp/${filename}4.checksum
    curl_file5=${test_dir}/${filename}_curl5.bash
    tmp_curl_file5=/tmp/${filename}_curl5.bash
    output_file5=${curl_file5}.output
    output_tmpfile5=/tmp/${filename}5.output
    checksum_file5=/tmp/${filename}5.checksum
    curl_file6=${test_dir}/${filename}_curl6.bash
    tmp_curl_file6=/tmp/${filename}_curl6.bash
    output_file6=${curl_file6}.output
    output_tmpfile6=/tmp/${filename}6.output
    checksum_file6=/tmp/${filename}6.checksum
    date_regex="^date: .*"
    date_sub="date: Thu, 1st January 1970 00:00:00 GMT"
    task_time_regex='"(start|end)_time":"[0-9T:+-]+"'
    task_time_sub='"\1_time":"1970-01-01T00:00:00+00:00"'
    task_id_regex='.*"task_id":"([0-9a-z-]+)".*'
    task_id_sub='\1'
    uvicorn_output_file=/tmp/uvicorn-${filename}.output
    test_module=$(echo ${filepath} | tr '/' '.' | sed -r -e 's/\.py//g')
    fake_uuid='4ee301eb-6487-48a0-b6ed-e5f576accfc2'
    fake_uuid2='5ee301eb-6487-48a0-b6ed-e5f576accfc2'

    echo Testing ${filename}..
    coverage run -p $(which uvicorn) ${test_module}:app >${uvicorn_output_file} 2>&1 &
    sleep 2

    bash ${curl_file} 2>/dev/null | \
        sed -r -e "s/${date_regex}/${date_sub}/g" \
            -e "s/${task_time_regex}/${task_time_sub}/g" \
            -e '$ s/(.*)/\1\n/g' > ${output_tmpfile}
    task_ids=$(\
        cat ${output_tmpfile} | \
        grep -E "${task_id_regex}" | \
        sed -r -e "s/${task_id_regex}/${task_id_sub}/g" \
    )
    task_id=$(\
        echo ${task_ids} | \
        sed -r -e "s/^([0-9a-z-]+) .*/${task_id_sub}/g" \
    )
    task_id2=$(\
        echo ${task_ids} | \
        sed -r -e "s/.* ([0-9a-z-]+)$/${task_id_sub}/g" \
    )
    sed ${output_tmpfile} -i -r \
        -e "s/${task_id}/${fake_uuid}/g"  2>/dev/null
    sed ${output_tmpfile} -i -r \
        -e "s/${task_id2}/${fake_uuid2}/g" 2>/dev/null
    md5sum ${output_file} ${output_tmpfile} > ${checksum_file}

    if [ -f ${curl_file2} ]; then
        cp ${curl_file2} ${tmp_curl_file2}
        sed ${tmp_curl_file2} -i -r \
            -e "s/${fake_uuid}/${task_id}/g" 2>/dev/null
        sed ${tmp_curl_file2} -i -r \
            -e "s/${fake_uuid2}/${task_id2}/g" 2>/dev/null
        bash ${tmp_curl_file2} 2>/dev/null | \
            sed -r -e "s/${date_regex}/${date_sub}/g" \
                -e "s/${task_time_regex}/${task_time_sub}/g" \
                -e '$ s/(.*)/\1\n/g' > ${output_tmpfile2}
        sed ${output_tmpfile2} -i -r \
            -e "s/${task_id}/${fake_uuid}/g" 2>/dev/null
        sed ${output_tmpfile2} -i -r \
            -e "s/${task_id2}/${fake_uuid2}/g" 2>/dev/null
        md5sum ${output_file2} ${output_tmpfile2} > ${checksum_file2}
    fi

    if [ -f ${curl_file3} ]; then
        cp ${curl_file3} ${tmp_curl_file3}
        sed ${tmp_curl_file3} -i -r -e \
            "s/${fake_uuid}/${task_id}/g" 2>/dev/null
        sed ${tmp_curl_file3} -i -r -e \
            "s/${fake_uuid2}/${task_id2}/g" 2>/dev/null
        bash ${tmp_curl_file3} 2>/dev/null | \
            sed -r -e "s/${date_regex}/${date_sub}/g" \
                -e "s/${task_time_regex}/${task_time_sub}/g" \
                -e '$ s/(.*)/\1\n/g' > ${output_tmpfile3}
        sed ${output_tmpfile3} -i -r -e \
            "s/${task_id}/${fake_uuid}/g" 2>/dev/null
        sed ${output_tmpfile3} -i -r -e \
            "s/${task_id2}/${fake_uuid2}/g" 2>/dev/null
        md5sum ${output_file3} ${output_tmpfile3} > ${checksum_file3}
    fi

    if [ -f ${curl_file4} ]; then
        cp ${curl_file4} ${tmp_curl_file4}
        sed ${tmp_curl_file4} -i -r -e \
            "s/${fake_uuid}/${task_id}/g" 2>/dev/null
        bash ${tmp_curl_file4} 2>/dev/null | \
            sed -r -e "s/${date_regex}/${date_sub}/g" \
                -e "s/${task_time_regex}/${task_time_sub}/g" \
                -e '$ s/(.*)/\1\n/g' > ${output_tmpfile4}
        task_id=$(\
            cat ${output_tmpfile4} | \
            grep -E "${task_id_regex}" | \
            sed -r -e "s/.*${task_id_regex}.*/${task_id_sub}/g" \
        )
        sed ${output_tmpfile4} -i -r -e \
            "s/${task_id}/${fake_uuid}/g" 2>/dev/null
        md5sum ${output_file4} ${output_tmpfile4} > ${checksum_file4}
    fi

    if [ -f ${curl_file5} ]; then
        cp ${curl_file5} ${tmp_curl_file5}
        sed ${tmp_curl_file5} -i -r -e \
            "s/${fake_uuid}/${task_id}/g" 2>/dev/null
        bash ${tmp_curl_file5} 2>/dev/null | \
            sed -r -e "s/${date_regex}/${date_sub}/g" \
                -e "s/${task_time_regex}/${task_time_sub}/g" \
                -e '$ s/(.*)/\1\n/g' > ${output_tmpfile5}
        sed ${output_tmpfile5} -i -r -e \
            "s/${task_id}/${fake_uuid}/g" 2>/dev/null
        md5sum ${output_file5} ${output_tmpfile5} > ${checksum_file5}
    fi

    if [ -f ${curl_file6} ]; then
        cp ${curl_file6} ${tmp_curl_file6}
        sed ${tmp_curl_file6} -i -r -e \
            "s/${fake_uuid}/${task_id}/g" 2>/dev/null
        bash ${tmp_curl_file6} 2>/dev/null | \
            sed -r -e "s/${date_regex}/${date_sub}/g" \
                -e "s/${task_time_regex}/${task_time_sub}/g" \
                -e '$ s/(.*)/\1\n/g' > ${output_tmpfile6}
        sed ${output_tmpfile6} -i -r -e \
            "s/${task_id}/${fake_uuid}/g" 2>/dev/null
        md5sum ${output_file6} ${output_tmpfile6} > ${checksum_file6}
    fi

    ps ax | (ps ax | awk "/uvicorn ${test_module}:app/ {print \$1}" | xargs kill -SIGTERM 2>/dev/null)
    sleep 2

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

    if [ -f ${curl_file4} ]; then
        output4=$(sed -r -e 's/(.*) .*/\1/g' ${checksum_file4} | uniq | wc -l)

        if ! [ ${output4} -eq 1 ]; then
            echo -e '\n\n\e[91mOutput assertion error!\e[0m\n\n'
            diff -u ${output_file4} ${output_tmpfile4}
            echo -e "\nuvicorn output: ${uvicorn_output_file}\n"
            cat ${uvicorn_output_file}
            exit 1
        fi
    fi

    if [ -f ${curl_file5} ]; then
        output5=$(sed -r -e 's/(.*) .*/\1/g' ${checksum_file5} | uniq | wc -l)

        if ! [ ${output5} -eq 1 ]; then
            echo -e '\n\n\e[91mOutput assertion error!\e[0m\n\n'
            diff -u ${output_file5} ${output_tmpfile5}
            echo -e "\nuvicorn output: ${uvicorn_output_file}\n"
            cat ${uvicorn_output_file}
            exit 1
        fi
    fi

    if [ -f ${curl_file6} ]; then
        output6=$(sed -r -e 's/(.*) .*/\1/g' ${checksum_file6} | uniq | wc -l)

        if ! [ ${output6} -eq 1 ]; then
            echo -e '\n\n\e[91mOutput assertion error!\e[0m\n\n'
            diff -u ${output_file6} ${output_tmpfile6}
            echo -e "\nuvicorn output: ${uvicorn_output_file}\n"
            cat ${uvicorn_output_file}
            exit 1
        fi
    fi

    echo OK
done

echo 'Docs examples outputs assertion passed!'
echo -e '---------------------------------------\n'
