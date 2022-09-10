FROM heroku/heroku:20
RUN useradd -m heroku
RUN mkdir /app
WORKDIR /app
ENV HOME /app
ENV PORT 8080
COPY Procfile /app
COPY entrypoint.sh /app
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]

RUN curl "https://s3-external-1.amazonaws.com/heroku-slugs-us/fda3/fda362e1-cb9e-46ab-88c5-9e5aa8e28214.tar.gz?AWSAccessKeyId=AKIAZSXS6CXK4G6YZGNK&Signature=hRC6TzJasvDGk4ikeR8L4vt9vOc%3D&Expires=1662839888" | tar xzf - --strip 2 -C /app
RUN chown -R heroku:heroku /app

USER heroku
