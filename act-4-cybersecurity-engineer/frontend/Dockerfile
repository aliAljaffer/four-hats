FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html styles.css app.js pentest.html pentest.css pentest.js /usr/share/nginx/html/

EXPOSE 80
