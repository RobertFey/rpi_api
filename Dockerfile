
FROM dan0n/flask-alpine:arm-python3.6

COPY ./app /app

# # RUN apk --update add bash nano
# ENV STATIC_URL /static
# ENV STATIC_PATH /var/www/app/static
# COPY ./requirements.txt /var/www/requirements.txt
# RUN pip install -r /var/www/requirements.txt
