FROM node:lts

WORKDIR /app
ADD . ./

RUN apt update -y && \
  apt upgrade -y && \
  yarn install --production=false
