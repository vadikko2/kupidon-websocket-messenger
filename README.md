# websocket-messenger

Сервис для обмена моментальными сообщениями.

## Установка

```bash
python3.12 -m venv venv
make install
```

## Запуск

### Локальный запуск

```bash
make run
```

### Запуск в docker-compose

```bash
make docker-up
make docker-down
```

## Настройка среды разработки

### Установка зависимостей

```bash
make dev
```

### Настройка `pre-commit`

```bash
make pre-commit
```
