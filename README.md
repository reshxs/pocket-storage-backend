# Pocket Storage
`Версия python - 3.10.4`
# Разработка
По умолчанию приложение доступно по `localhost:8000`
## Запуск в Docker
### Поднять приложение с окружением
```bash
$ docker compose -f dev.docker-compose.yml up -d
```
### Поднять окружение
```bash
$ docker compose up -d
```
## Запуск без docker
### Подготовка окружения
```bash
$ python3 -m venv .venv
$ . ./.venv/scripts/activate
$ python3 -m pip install -r src/requirements.txt 
```
### Запуск приложения
```bash
$ python3 src/run.py web --collectstatic --migrate
```
## Доступ к панели администратора
Панель администратора доступна по `localhost:8000/app/admin`
### Создание админа
```bash
$ python3 src/manage.py createsuperuser
```
## Генерация тестовых данных
```bash
python3 src/manage.py generate_test_data 
```
