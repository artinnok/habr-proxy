# Хабр прокси

## Зависимости Python

* [requests](http://docs.python-requests.org/en/master/)
* [lxml](http://lxml.de/)
* [click](http://click.pocoo.org/5/)


## Установка

Теперь и далее считается, что у вас стоит UNIX-like система

1. Клонируем проект: `git clone https://github.com/artinnok/habr-proxy.git`
2. Ставим виртуальное окружение: `virtualenv -p python3 env`
3. Активируем виртуальное окружение: `source env/bin/activate`
4. Ставим пакеты для lxml:
```bash
sudo apt-get install python3-lxml python-lxml libxml2-dev libxslt-dev python-dev lib32z1-dev
```
5. Установим зависимости: `pip install -r requirements.txt`
6. Стартуем прокси - сервер: `python3 proxy.py`

Можно посмотреть параметры прокси - сервера: `python3 proxy.py --help`