FROM node:16.14.2-alpine3.14

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY ./package.json .
RUN npm install

# copy project
COPY . .
