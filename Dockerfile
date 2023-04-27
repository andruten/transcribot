FROM python:3.10-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update -qqq && \
    apt install \
      --no-install-recommends --no-install-suggests -y -qqq \
      ffmpeg && \
    mkdir /opt/app && \
    mkdir /opt/requirements

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

COPY ./requirements /opt/requirements/

WORKDIR /opt/app

ARG requirements
RUN pip install --upgrade pip &&  \
    pip install -r /opt/requirements/${requirements:-"pro"}.txt

# Copy code
COPY . .

CMD python -m main
