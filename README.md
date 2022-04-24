# netology-final-diplom
API сервис заказа товаров для розничных сетей

[**Документация по API**](https://documenter.getpostman.com/view/13651797/UVyvuZpb)

***

## Инструкция по запуску

* Создать и заполнить **_.env_** файл в директории **_netology-final-diplom_**
```
SECRET_KEY=your_secret_key

POSTGRES_USER=root
POSTGRES_PASSWORD=root
POSTGRES_DB=orders

DB_HOST=database
DB_PORT=5432

EMAIL_HOST=smtp.yandex.ru
EMAIL_HOST_USER=email@host.ru
EMAIL_HOST_PASSWORD=password
EMAIL_PORT=465
```
* В директории **_netology-final-diplom_** выполнить `docker-compose up --build -d`

### Сервисы будут запущены на этих портах

* Backend: 127.0.0.1:8000
* Frontend: 127.0.0.1:8080