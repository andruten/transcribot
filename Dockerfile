FROM python:3.12.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt update -qqq && \
    apt install \
      --no-install-recommends --no-install-suggests -y -qqq \
      ffmpeg

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./requirements /opt/requirements/

WORKDIR /opt/app

ARG requirements
RUN pip install --upgrade pip && \
    pip install -r /opt/requirements/${requirements:-"pro"}.txt

# Copy code
COPY . .

ENV HF_HOME=/root/.cache/whisper

CMD ["python", "-m", "main"]
