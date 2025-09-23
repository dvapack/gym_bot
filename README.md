# Gym bot

**Telegram бот для ведения прогресса тренировок в зале**

## Database


| User        | Workout  | Exercise     | Set          |
| ----------- | -------- | ------------ | ------------ |
| PK: id      | PK: id   | PK: id       | PK: id       |
| FK: workout | FK: user | muscle_group | FK: workout  |
|             | date     | name         | FK: exercise |
|             |          |              | set_order    |
|             |          |              | weight       |
|             |          |              | reps         |

### Queries

1. ~~Создать пользователя~~
2. ~~Получить пользователя~~
3. ~~Создать тренировку~~
4. Создать упражнение
5. Получить группы мышц
6. Получить упражнение
7. ~~Создать подход~~
8. ~~Получить тренировку~~
