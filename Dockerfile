FROM python:3.10-slim-bullseye

RUN apt update -qqq && apt install \
      --no-install-recommends --no-install-suggests -y -qqq \
      ffmpeg \
      git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get clean \
    && mkdir /opt/app \
    && addgroup --gid 1000 apprunner \
    && adduser --system --disabled-password --disabled-login --gecos "" --gid 1000 --uid 1000 apprunner \
    && chown -R apprunner:apprunner /opt/app \
    && chsh -s /bin/false apprunner

# Requirements
RUN pip install --upgrade pip

USER apprunner

WORKDIR /opt/app

ENV PATH="/home/apprunner/.local/bin:${PATH}"
COPY ./requirements/ /opt/requirements/
ARG requirements
RUN pip install -r /opt/requirements/${requirements:-"pro"}.txt

# Copy code
COPY . .

CMD python -m main
