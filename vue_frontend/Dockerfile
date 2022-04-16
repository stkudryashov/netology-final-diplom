FROM node:16.14.2-alpine3.14

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY ./package.json .
RUN npm i && npm i @vue/cli -g

# copy project
COPY . .
