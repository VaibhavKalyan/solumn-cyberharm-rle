FROM python:3.12.8-slim-bookworm@sha256:2199a62885a12290dc9c5be3ca0681d367576ab7bf037da120e564723292a2f0
RUN apt-get update && apt-get install -y --no-install-recommends tmux curl git procps \
    && pip install --no-cache-dir playwright==1.56.0 \
    && PLAYWRIGHT_BROWSERS_PATH=/opt/browsers python -m playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --uid 1000 --shell /bin/bash agent
WORKDIR /app
COPY repo/ /app/
COPY provider_service.py entrypoint.sh /opt/cedar/
RUN chown -R agent:agent /app && chmod 755 /opt/cedar/entrypoint.sh
RUN python3 -c "import pathlib,hashlib,json; pathlib.Path('/opt/cedar/baseline.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in pathlib.Path('/app').rglob('*') if p.is_file()}))"
ENV PYTHONDONTWRITEBYTECODE=1 PLAYWRIGHT_BROWSERS_PATH=/opt/browsers
ENTRYPOINT ["/opt/cedar/entrypoint.sh"]
CMD ["sleep", "infinity"]
