FROM python:3.11-slim
RUN useradd -m -u 10001 appuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -U "urllib3>=2.8.0" "msgpack>=1.2.1" "setuptools>=78.1.1" "wheel>=0.46.2" "jaraco.context>=6.1.0" && \
    pip uninstall -y setuptools wheel
COPY . .
USER 10001
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
