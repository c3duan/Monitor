#!/usr/local/bin/bash
# Pretty colors!
RED='\e[31m'
GREEN='\e[32m'
NC='\e[0m' # No Color

echo -e "${GREEN}Creating${NC} docker network";
docker network create --driver=bridge monitor_network;

###################
# MYSQL CONTAINER #
###################

echo -e "${GREEN}Removing${NC} Active Database Container";
docker rm -f monitor_db;

echo -e "${GREEN}Removing${NC} Existing Database Image";
docker rmi monitor_db;

echo -e "${GREEN}Creating${NC} Image";
docker build -t monitor_db sql;

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

echo -e "${GREEN}Creating${NC} Container";
docker run --name="${REQUIRED_ENV_VARS[DB_DATABASE]}" --net=monitor_network -e MYSQL_ROOT_PASSWORD="${REQUIRED_ENV_VARS[DB_PASSWORD]}" -v monitor_db_volume:/var/lib/mysql -d monitor_db;
sleep 30;
docker exec monitor_db mysql -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'SET GLOBAL local_infile = 1;';
docker exec monitor_db mysql -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e "ALTER USER '${REQUIRED_ENV_VARS[DB_USERNAME]}'@'${REQUIRED_ENV_VARS[DB_HOST]}' IDENTIFIED WITH mysql_native_password BY '${REQUIRED_ENV_VARS[DB_PASSWORD]}'; FLUSH PRIVILEGES;";

echo -e "${GREEN}Populating${NC} Database [${RED}This takes super long :(${NC}]";
docker exec monitor_db mysql --local-infile=1 -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'source /home/monitor_db/create_tables.sql;';

echo -e "${GREEN}Creating${NC} Feature Vectors";
echo "1. Spliting Streams ...";
docker exec monitor_db python3 /home/monitor_db/events/src/split_streams.py;
echo "2. Extracting Features ...";
docker exec monitor_db python3 /home/monitor_db/events/src/feature_extractor.py;
echo "3. Creating Event Table";
docker exec monitor_db mysql --local-infile=1 -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'source /home/monitor_db/events/data/vector/event_table.sql;';
echo "4. Creating Vector Table";
docker exec monitor_db mysql --local-infile=1 -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'source /home/monitor_db/events/data/vector/hcdm_vector_table.sql;';

echo -e "${GREEN}Creating${NC} Split Feature Vectors";
echo "1. Reducing Feature Vectors ...";
docker exec monitor_db chmod a+x /home/monitor_db/events/data/vector/parallel/reduce.sh
docker exec monitor_db /bin/sh /home/monitor_db/events/data/vector/parallel/reduce.sh "${REQUIRED_ENV_VARS[DB_USERNAME]}" "${REQUIRED_ENV_VARS[DB_DATABASE]}" "${REQUIRED_ENV_VARS[DB_PASSWORD]}"
echo "2. Splitting Feature Vectors ...";
docker exec monitor_db python3 /home/monitor_db/events/src/split_feature_extractor.py;
docker cp monitor_db:/home/monitor_db/events/src/data.py ./monitor-api/routes/event_vectors/;
docker cp monitor_db:/home/monitor_db/events/src/normalizer.save ./monitor-api/routes/event_vectors/;
docker exec monitor_db mysql --local-infile=1 -h "${REQUIRED_ENV_VARS[DB_HOST]}" -u "${REQUIRED_ENV_VARS[DB_USERNAME]}" -p${REQUIRED_ENV_VARS[DB_PASSWORD]} -e 'source /home/monitor_db/events/data/vector/split/split_hcdm_vector_table.sql;';

#########################
# MONITOR API CONTAINER #
#########################

echo -e "${GREEN}Removing${NC} Active Container";
docker rm -f monitor_api;

echo -e "${GREEN}Removing${NC} Existing Backend Image";
docker rmi monitor_api;

echo -e "${GREEN}Copying${NC} .env file into monitor_api container";
cp .env monitor_api/;

echo -e "${GREEN}Creating${NC} Image";
docker build -t monitor_api monitor-api;
  
echo -e "${GREEN}Creating${NC} Container";
docker run -e TZ=America/New_York --name=monitor_api --net=monitor_network -p 3000:3000 -d monitor_api;

echo -e "${GREEN}Installing${NC} Python";
docker exec monitor_api apt-get update;
docker exec monitor_api apt-get -y install python3 python3-pip;
docker exec monitor_api pip3 install -U pip;
docker exec monitor_api pip install mysql-connector sklearn scipy tqdm numpy python-dotenv;
docker exec monitor_api pip install --user mysql-connector-python

###########################
# MONITOR FRONT CONTAINER #
###########################

echo -e "${GREEN}Removing${NC} Active Container";
docker rm -f monitor_front;

echo -e "${GREEN}Removing${NC} Existing Frontend Image";
docker rmi monitor_front;

echo -e "${GREEN}Creating${NC} Image";
docker build -t monitor_front monitor-front;

echo -e "${GREEN}Creating${NC} Container";
docker run --name=monitor_front --net=monitor_network -p 4200:4200 -d monitor_front;
