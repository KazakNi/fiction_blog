Литературный блог
<!-- О проекте -->
## О проекте

![image](https://sub-cult.ru/images/2021/KsDs/i.jpg)

Данный проект призван привлечь всех любителей литературы: сервис позволяет регистрироваться, вести свои записи, комментировать записи других членов клуба, подписываться на интересующих авторов. 

В нашем уголке нашли своё место отрывки из великих классиков, присоединяйтесь!

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/KazakNi/fiction_blog
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
