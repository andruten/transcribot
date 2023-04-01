FROM python:3.10-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

RUN chown -R apprunner:apprunner "$VIRTUAL_ENV"
COPY --chown=apprunner:apprunner ./requirements /opt/requirements/
RUN chown -R apprunner:apprunner /opt/app

USER apprunner

WORKDIR /opt/app

ARG requirements
RUN pip install --upgrade pip &&  \
    pip install -r /opt/requirements/${requirements:-"pro"}.txt

# Copy code
COPY --chown=apprunner:apprunner . .

CMD python -m main
