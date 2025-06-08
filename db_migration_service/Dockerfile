FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

RUN npm run build
RUN npm install dotenv --save

CMD ["npm", "run", "migration:run"]
