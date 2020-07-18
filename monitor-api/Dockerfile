FROM node:10.13
WORKDIR /home/monitor_api
COPY package*.json ./
RUN apt-get update && apt-get -y install sudo
RUN sudo npm install
RUN sudo npm install nodemon -g
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
