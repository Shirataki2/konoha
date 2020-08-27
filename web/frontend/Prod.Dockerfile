FROM node:lts-alpine

WORKDIR /app
RUN rm -rf node_modules && \
    rm -rf .nuxt
COPY package.json yarn.lock ./
RUN yarn install --production=false

COPY . .

RUN cat .env
RUN set -a && source .env && set +a && \
    yarn build --no-cache

EXPOSE 3000
CMD ["yarn", "start"]