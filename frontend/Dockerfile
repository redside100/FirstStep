FROM node:latest

WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH

COPY firststep-fe/package.json .
COPY firststep-fe/package-lock.json .
RUN npm install

COPY firststep-fe .
CMD ["npm", "run", "start-prod"]