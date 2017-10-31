FROM node:latest

WORKDIR /var/app

COPY . .

RUN npm install

ENV APP_ENV=docker

CMD [ "npm", "start" ]
