FROM node:lts

WORKDIR /app

RUN apt update -y && \
  apt upgrade -y && \
  yarn install --production=false
