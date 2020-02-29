#!/bin/bash
path=$(cd "$(dirname "$0")"; pwd -P)
dir="$(dirname "$path")"
file="${dir}/hcdm_vectors_reduced.csv"
echo "${3}"

mysql -u "${1}" -D "${2}" -p${3} -e 'SELECT * FROM hcdm_vectors;' | sed $'s/\t/,/g' > $file;
# mysql -u "${1}" -D "${2}" -p${3} -e 'SELECT * FROM hcdm_vectors;' | sed 's/\t/,/g' > $file;
