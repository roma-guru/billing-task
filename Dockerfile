from python:3.9-slim
expose 8000
workdir /app
copy . .

run apt update && apt install -y build-essential libpq-dev musl-dev libffi-dev && pip3 install poetry
run poetry install

cmd ["poetry","run","uvicorn","app:app","--host","0.0.0.0"]
