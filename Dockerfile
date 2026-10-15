FROM python:3.12.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./requirements /opt/requirements/

WORKDIR /opt/app

ARG requirements=pro
ARG whisper_model=""
RUN pip install --upgrade pip && \
    pip install -r /opt/requirements/${requirements}.txt

# Optionally download the CTranslate2 model into the image so containers
# start instantly without a network fetch to the HF Hub. Put it before
# COPY . . so code changes don't invalidate the model layer.
ENV HF_HOME=/root/.cache/whisper
RUN if [ -n "${whisper_model}" ]; then \
      python -c "from faster_whisper import WhisperModel; WhisperModel('${whisper_model}', device='cpu', compute_type='int8')"; \
    fi

# Copy code
COPY . .

CMD ["python", "-m", "main"]
