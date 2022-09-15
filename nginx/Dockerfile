FROM nginx

COPY nginx.conf /etc/nginx
COPY nginx.conf /etc/nginx/conf.d

EXPOSE 80

STOPSIGNAL SIGQUIT

CMD ["nginx", "-g", "daemon off;"]
