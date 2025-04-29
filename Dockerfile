# Определяем базовый образ:
FROM python:3.9-alpine3.16
# Копируем файл зависимостей в временную директорию:
COPY requirements.txt /temp/requirements.txt
# Копируем код приложения в корень контейнера:
COPY service /service
# Определяем рабочую директорию:
WORKDIR /service
# Порт, который будет использоваться приложением:
EXPOSE 8000
# Устанавливаем зависимости:
RUN pip install -r /temp/requirements.txt
# Cоздаем пользователя для запуска приложения:
RUN adduser --disabled-password service-user
# Устанавливаем права на директорию приложения:
USER service-user