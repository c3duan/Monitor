FROM node:10.13
WORKDIR /home/monitor_api
COPY package*.json ./
RUN npm install
RUN npm install nodemon -g
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
