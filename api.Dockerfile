FROM python:3.12

RUN apt-get update &&\
    apt-get install -y libgdal-dev gdal-bin

RUN gdal-config --version

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./scripts /code/scripts
COPY ./data /code/data

RUN wget https://storage.googleapis.com/off-grid-440012.appspot.com/data/ncat-10.tif 

COPY ./src/off_grid /code/src/off_grid

ENV PORT=8000

CMD exec fastapi run src/off_grid/main.py --port $PORT

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]
