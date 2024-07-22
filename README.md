# currency_bot
Для запуска на своем компьютере скачайте код:
```text
git clone git@github.com:NovikovMU/currency_bot.git
```
Перейдите в папку
```text
cd currency_bot
```
Создайте виртуальное окружение и внесите ваш бот токен
```text
nano .env
BOT_API=<Ваш бот токен>
```
Запустите докер файл (должен быть на машине установлен docker engine)
```text
docker compose up -d
```