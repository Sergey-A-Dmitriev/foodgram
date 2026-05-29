FROM nginx:1.25.4-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY openapi-schema.yml /usr/share/nginx/html/docs/
COPY redoc.html /usr/share/nginx/html/docs/
