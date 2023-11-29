FROM python:3.9-slim
COPY requirements.txt /tmp/requirements.txt

RUN apt update &&  \
    apt install build-essential curl ca-certificates gnupg -y
RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get install -y nodejs
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
EXPOSE 8080
ENTRYPOINT ["bash", "-c", "pip3 install --no-cache-dir -r requirements.txt && python app.py"]
