FROM node:24-alpine AS build
WORKDIR /app
RUN npm install --global pnpm@11.15.1
COPY apps/law-agent-web/package.json apps/law-agent-web/pnpm-lock.yaml* ./
RUN pnpm install --no-frozen-lockfile
COPY apps/law-agent-web ./
RUN pnpm build

FROM node:24-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S app && adduser -S app -G app
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
USER app
EXPOSE 3000
CMD ["node", "server.js"]
