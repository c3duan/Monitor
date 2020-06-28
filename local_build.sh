#!/usr/local/bin/bash
# Pretty colors!
RED='\e[31m'
GREEN='\e[32m'
NC='\e[0m' # No Color

###################
# MYSQL CONTAINER #
###################

echo -e "${GREEN}Reading${NC} and ${GREEN}Verifying${NC} .env variables ...";

ENV_FILE=".env"
declare -A REQUIRED_ENV_VARS=( [DB_HOST]="" [DB_DATABASE]="" [DB_USERNAME]="" [DB_PASSWORD]="" )
ERRORS_EXIST=false
# Verify that the required entries in the .env file exist (and are not set to empty strings)
for i in "${!REQUIRED_ENV_VARS[@]}"
do
    :
    if ! grep -qoEx "${i}=.+" "${ENV_FILE}"; then
        echo -e "${RED}Error:${NC} Missing required line from your .env file: \"$i={your_value}\"\n"
        ERRORS_EXIST=true
    else
        REQUIRED_ENV_VARS[$i]=`grep -oEx "${i}=.+" "${ENV_FILE}" | sed -n -e "s/^.*${i}=//p"`
    fi
done

if [ ${ERRORS_EXIST} == true ]; then
    exit 0;
fi

echo -e "${GREEN}Creating${NC} Monitor Database";
mysql -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'SET GLOBAL local_infile = 1;';
mysql -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e "ALTER USER '${REQUIRED_ENV_VARS[DB_USERNAME]}' IDENTIFIED WITH mysql_native_password BY '${REQUIRED_ENV_VARS[DB_PASSWORD]}'; FLUSH PRIVILEGES;";

echo -e "${GREEN}Populating${NC} Monitor Database [${RED}This takes super long :(${NC}]";
mysql --local-infile=1 -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'source ./sql/create_tables.sql;';


echo -e "${GREEN}Populating${NC} Aniyama Database"
python3 ./sql/events/src/aniyama_data_processor.py;
mysql --local-infile=1 -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'source ./sql/create_aniyama_tables.sql;';

echo -e "${GREEN}Creating${NC} Feature Vectors";
echo "1. Spliting Streams ...";
python3 ./sql/events/src/split_streams.py;
python3 ./sql/events/src/split_streams.py /../../data/vector/aniyama/aniyama_data.csv;
echo "2. Extracting Features ...";
python3 ./sql/monitor_db/events/src/feature_extractor.py;
echo "3. Creating Event Table";
mysql --local-infile=1 -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'source ./sql/events/data/vector/event_table.sql;';
echo "4. Creating Vector Table";
mysql --local-infile=1 -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'source ./sql/events/data/vector/hcdm_vector_table.sql;';

echo -e "${GREEN}Creating${NC} Split Feature Vectors";
echo "1. Reducing Feature Vectors ...";
chmod a+x ./sql/events/data/vector/parallel/reduce.sh
/bin/sh ./sql/events/data/vector/parallel/reduce.sh "${REQUIRED_ENV_VARS[DB_USERNAME]}" "${REQUIRED_ENV_VARS[DB_DATABASE]}" "${REQUIRED_ENV_VARS[DB_PASSWORD]}"
echo "2. Splitting Feature Vectors ...";
python3 ./sql/events/src/split_feature_extractor.py;
cp ./sql/events/src/data.py ./monitor-api/routes/event_vectors/;
cp ./sql/events/src/normalizer.save ./monitor-api/routes/event_vectors/;
mysql --local-infile=1 -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'source ./sql/events/data/vector/split/split_hcdm_vector_table.sql;';
