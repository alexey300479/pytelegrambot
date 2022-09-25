---
created: 2022-09-14T08:30:52.343Z
updated: 2022-09-14T11:20:35.436Z
assigned: Киселев
progress: 1
tags: []
started: 2022-09-14T00:00:00.000Z
completed: 2022-09-14T00:00:00.000Z
---

# Создать в базе данных tobibot_db таблицы для хранения информации о резидентах бизнес-инкубатора и отраслях пользуясь функционалом Django

Поля таблицы resident:
- tg_user_id - int - index
- first_name - str
- last_name - str
- phone - str
- birthdate - date
- photo - (url)
- socials - str (url)
- company - str
- branch_id - foreign key (table branches)
- description- str

Поля таблицы branch:
- id - index
- name - str
