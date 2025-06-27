FROM python:3.12-slim

LABEL maintainer="Jaroslaw Stakun <jstakun@redhat.com>" \
      io.k8s.display-name="Voice TTS Python 3.12"

# Environment
ENV COQUI_TOS_AGREED=1 \
    VENV_PATH=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    TTS_HOME=/opt/tts_home 

# Set working directory
WORKDIR /opt/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends git ffmpeg espeak-ng libsndfile1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 1000 --gid 0 -ms /bin/bash appuser \
    && mkdir /opt/venv /opt/tts_home \
    && chown -R appuser:0 /opt/app /opt/venv /opt/tts_home \
    && chmod -R g+w /opt/app /opt/venv /opt/tts_home

# Switch to non-root user
USER appuser

# Create and activate virtual environment + install Python packages
RUN python3 -m venv $VENV_PATH \
    && $VENV_PATH/bin/pip install --upgrade pip \
    && $VENV_PATH/bin/pip install fastapi uvicorn coqui-tts \
    && python3 -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2')"

# Copy server code
COPY server.py .

EXPOSE 5000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5000"]

