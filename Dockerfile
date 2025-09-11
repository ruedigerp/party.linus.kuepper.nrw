# ghcr.io/ruedigerp/esc-essen:v0.0.13
# FROM nginx

# COPY public /usr/share/nginx/html

FROM nginx
COPY hugo/esc/public/ /usr/share/nginx/html/