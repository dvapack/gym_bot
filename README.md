# Gym bot

![Funny pic](./etc/funny_pic.jpg)

**Telegram бот для ведения прогресса тренировок в зале**

## Database

| User        | Workout  | Exercise     | Set          |
| ----------- | -------- | ------------ | ------------ |
| PK: id      | PK: id   | PK: id       | PK: id       |
| FK: workout | FK: user | FK: user     | FK: workout  |
|             | date     | muscle_group | FK: exercise |
|             |          | name         | set_order    |
|             |          |              | weight       |
|             |          |              | reps         |

### Queries

1. ~~Создать пользователя~~
2. ~~Получить пользователя~~
3. ~~Создать тренировку~~
4. ~~Создать упражнение~~
5. ~~Получить группы мышц~~
6. ~~Получить упражнения~~
7. ~~Создать подход~~
8. Получить тренировку
