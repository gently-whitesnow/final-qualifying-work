# Runbook стенда ВКР

## Ветка

Работа ведется в ветке проекта:

`thesis/realtime-scaleout`

Корневой репозиторий проекта:

`/Users/gently/projects/bugreport-root/bugget`

В материалах ВКР стенд описывается как `app-api`: это изолированный контур проверки real-time масштабирования, не зависящий от дополнительных продуктовых сервисов и полноценного пользовательского интерфейса.

## Основной стенд с Redis backplane

```bash
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml up -d --build
```

Состав стенда:

- `postgres_app_thesis`;
- `redis_app_thesis`;
- `app-api-1`;
- `app-api-2`;
- `nginx_app_thesis`.

Быстрая проверка nginx-входа:

```bash
curl -sS http://localhost:18080/health
```

Ожидаемый результат:

```text
ok
```

## Стенд без Redis backplane

Этот режим нужен, чтобы показать исходное ограничение multi-instance архитектуры без межузловой доставки.

```bash
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml -f docker-compose.thesis.no-backplane.yml up -d --build
```

## Остановка стенда

```bash
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml down -v --remove-orphans
```

Если запускался режим без backplane:

```bash
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml -f docker-compose.thesis.no-backplane.yml down -v --remove-orphans
```

## Базовая логика проверки

1. Запустить режим без backplane.
2. Подключить проверочный клиент A к `app-api-1`.
3. Подключить проверочный клиент B к `app-api-2`.
4. Выполнить изменение сущности отчета через `app-api-1`.
5. Зафиксировать, что событие не доставляется клиенту на `app-api-2`.
6. Запустить режим с Redis backplane.
7. Повторить тот же сценарий.
8. Зафиксировать, что событие доставляется между узлами.

## Автоматизированная проверка межузловой доставки

После запуска стенда можно выполнить сценарий, который:

- создает отчет через `app-api-1`;
- подключает один SignalR-клиент к `app-api-1`;
- подключает второй SignalR-клиент к `app-api-2`;
- подписывает обоих клиентов на группу отчета;
- меняет заголовок отчета через `app-api-1`;
- проверяет, получил ли клиент на `app-api-2` событие `ReceiveReportPatch`;
- измеряет задержку доставки события;
- выводит `serverInstanceId`, `connectionId`, идентификатор отчета, payload полученного события и метрики.

Команда из корня проекта:

```bash
cd /Users/gently/projects/bugreport-root/bugget
node scripts/realtime-scaleout-check.mjs
```

Ожидаемая интерпретация:

- в режиме с Redis backplane скрипт должен завершиться успешно и вывести JSON с `ok: true`;
- в режиме без backplane скрипт должен не дождаться события на втором узле, что демонстрирует исходное ограничение.

Для серийной проверки можно задать число итераций:

```bash
cd /Users/gently/projects/bugreport-root/bugget
THESIS_ITERATIONS=5 node scripts/realtime-scaleout-check.mjs
```

В этом режиме скрипт выводит `successful`, `failed` и агрегированные задержки доставки: `min`, `max`, `avg`, `p50`, `p95`.

Для проверки восстановления подписки после разрыва:

```bash
cd /Users/gently/projects/bugreport-root/bugget
THESIS_SCENARIO=rejoin node scripts/realtime-scaleout-check.mjs
```

Для проверки отказа одного экземпляра через nginx:

```bash
cd /Users/gently/projects/bugreport-root/bugget
THESIS_SCENARIO=failover THESIS_ALLOW_DOCKER_CONTROL=1 THESIS_TIMEOUT_MS=20000 node scripts/realtime-scaleout-check.mjs
```

Failover-сценарий намеренно требует `THESIS_ALLOW_DOCKER_CONTROL=1`, потому что он останавливает `app-api-2`, проверяет переподключение клиента к доступному узлу и затем запускает контейнер обратно.

## Полезные логи

```bash
docker logs app-api-1 --tail 200
docker logs app-api-2 --tail 200
docker logs nginx_app_thesis --tail 200
```

В логах должны быть видны:

- `ServerInstanceId`;
- `ConnectionId`;
- `GroupKey`;
- имя real-time события;
- `EventId` для отправленных событий.

## Проверки сборки и конфигурации

Docker Compose:

```bash
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml config --quiet
docker compose -f docker-compose.thesis.yml -f docker-compose.thesis.no-backplane.yml config --quiet
```

Backend:

```bash
cd /Users/gently/projects/bugreport-root/bugget/backend/bugget-api
dotnet build Bugget.sln
```
