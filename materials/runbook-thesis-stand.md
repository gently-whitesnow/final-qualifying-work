# Runbook стенда ВКР

## Ветка

Работа ведется в ветке проекта:

`thesis/realtime-scaleout`

Корневой репозиторий проекта:

`/Users/gently/projects/bugreport-root/bugget`

## Основной стенд с Redis backplane

```bash
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml up -d --build
```

Запуск фронтенда для демонстрации через nginx:

```bash
cd /Users/gently/projects/bugreport-root/bugget/frontend
VITE_SIGNALR_SKIP_NEGOTIATION=true npm run dev -- --host 0.0.0.0
```

Открывать:

`http://localhost:18080`

## Стенд без Redis backplane

Этот режим нужен, чтобы показать исходное ограничение multi-instance архитектуры без межузловой доставки.

```bash
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml -f docker-compose.thesis.no-backplane.yml up -d --build
```

Фронтенд запускать так же:

```bash
cd /Users/gently/projects/bugreport-root/bugget/frontend
VITE_SIGNALR_SKIP_NEGOTIATION=true npm run dev -- --host 0.0.0.0
```

## Остановка стенда

```bash
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml down -v
```

Если запускался режим без backplane:

```bash
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml -f docker-compose.thesis.no-backplane.yml down -v
```

## Что смотреть при демонстрации

В dev-режиме frontend показывает debug-badge в правом нижнем углу:

- идентификатор экземпляра backend;
- укороченный `connectionId`.

Это нужно для скриншотов и доказательства, что разные клиенты подключены к разным экземплярам `bugget-api`.

## Базовая логика проверки

1. Запустить режим без backplane.
2. Открыть два клиента и добиться подключения к разным узлам.
3. Выполнить изменение сущности отчета.
4. Зафиксировать, что событие не доставляется между узлами.
5. Запустить режим с Redis backplane.
6. Повторить тот же сценарий.
7. Зафиксировать, что событие доставляется между узлами.

## Автоматизированная проверка межузловой доставки

После запуска стенда можно выполнить сценарий, который:

- создает отчет через `bugget-api-1`;
- подключает один SignalR-клиент к `bugget-api-1`;
- подключает второй SignalR-клиент к `bugget-api-2`;
- подписывает обоих клиентов на группу отчета;
- меняет заголовок отчета через `bugget-api-1`;
- проверяет, получил ли клиент на `bugget-api-2` событие `ReceiveReportPatch`.

Команда:

```bash
cd /Users/gently/projects/bugreport-root/bugget/frontend
npm run test:realtime-scaleout
```

Ожидаемая интерпретация:

- в режиме с Redis backplane скрипт должен завершиться успешно и вывести JSON с `ok: true`;
- в режиме без backplane скрипт должен не дождаться события на втором узле, что демонстрирует исходное ограничение.

## Полезные логи

```bash
docker logs bugget-api-1 --tail 200
docker logs bugget-api-2 --tail 200
```

В логах должны быть видны:

- `ServerInstanceId`;
- `ConnectionId`;
- `GroupKey`;
- имя real-time события;
- `EventId` для отправленных событий.

## Проверки сборки

Backend:

```bash
cd /Users/gently/projects/bugreport-root/bugget/backend/bugget-api
dotnet build Bugget.sln
```

Frontend:

```bash
cd /Users/gently/projects/bugreport-root/bugget/frontend
npm run build
```
