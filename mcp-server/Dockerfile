FROM node:20-slim AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY tsconfig.json ./
COPY src/ ./src/

RUN npm run build

FROM node:20-slim

LABEL io.docker.server.metadata='name: youtube\ndescription: "YouTube MCP server for playlist management and video operations"\ncommand: ["node", "index.js"]'

WORKDIR /app

COPY package*.json ./

RUN npm install --omit=dev

COPY --from=build /app/dist ./dist/
COPY index.js ./

ENV NODE_ENV=production

ENTRYPOINT ["node", "index.js"]
