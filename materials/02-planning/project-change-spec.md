# Спецификация изменений в проекте под ВКР

## Цель изменений

Подготовить в отдельной ветке проекта воспроизводимую реализацию масштабируемого real-time контура для `bugget`, которая:

- устраняет ограничение single-node WebSocket-архитектуры;
- работает на минимальном multi-instance стенде;
- даёт наблюдаемые доказательства межузловой доставки событий;
- не требует мержить изменения в `main`.

## Что уже есть в проекте

### Backend

- SignalR уже подключён в [ServiceCollectionExtensions.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Extensions/ServiceCollectionExtensions.cs:136).
- Хаб уже опубликован по адресу [ApplicationBuilderExtensions.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Extensions/ApplicationBuilderExtensions.cs:24).
- Есть групповой хаб [ReportPageHub.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Hubs/ReportPageHub.cs:1).
- Есть централизованный отправитель real-time событий [ReportPageHubClient.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Hubs/ReportPageHubClient.cs:1).

### Frontend

- Клиент соединяется через SignalR и использует автоматическое переподключение [connection.ts](/Users/gently/projects/bugreport-root/bugget/frontend/src/shared/model/socket/connection.ts:1).
- После reconnect уже есть повторное вступление в группу отчета [useReportPageSocket.ts](/Users/gently/projects/bugreport-root/bugget/frontend/src/pages/Report/lib/useReportPageSocket.ts:1).
- Есть баннер деградации соединения [SystemBanner.tsx](/Users/gently/projects/bugreport-root/bugget/frontend/src/shared/ui/notifications/SystemBanner.tsx:1).

### Инфраструктура

- В корневом compose уже есть `redis`, но `bugget-api` пока не использует его как SignalR backplane [docker-compose.yml](/Users/gently/projects/bugreport-root/bugget/docker-compose.yml:1).
- В `nginx` upstream `app-api` пока содержит только один экземпляр `bugget-api` [upstreams.conf](/Users/gently/projects/bugreport-root/bugget/nginx/upstreams.conf:9).

## Что нужно реализовать

## 1. Изолированный стенд под ВКР

Лучше не ломать базовый сценарий запуска проекта. Поэтому под ВКР целесообразно добавить отдельный стенд, а не переписывать текущий `docker-compose.yml` как единственный вариант.

### Рекомендуемое решение

- добавить отдельный файл вида:
  - `docker-compose.thesis.yml`
  - или `docker-compose.scaleout.yml`
- в нём поднять:
  - `bugget-api-1`
  - `bugget-api-2`
  - при необходимости `bugget-api-3`
- оставить существующие `db`, `redis`, `nginx`, `frontend`, `users-api`, `authorization-api`

### Зачем так делать

- меньше риск сломать текущий локальный сценарий;
- удобнее показывать `до` и `после`;
- проще включать и выключать стенд ВКР;
- легче оформить это как отдельный артефакт в приложении к работе.

## 2. Подключение Redis backplane в backend

### Основные файлы

- [ServiceCollectionExtensions.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Extensions/ServiceCollectionExtensions.cs:136)
- [EnvironmentConstants.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget.Entities/Constants/EnvironmentConstants.cs:1)

### Что добавить

- новую переменную окружения для Redis, например:
  - `REDIS_CONNECTION_STRING`
- при необходимости переменную:
  - `SERVER_INSTANCE_ID`

### Что изменить в коде

- в `AddMessaging()` включить Redis backplane для SignalR;
- сделать это конфигурируемым, чтобы single-node режим без Redis тоже оставался возможным;
- не завязывать приложение жёстко на backplane во всех окружениях.

### Что важно для ВКР

- возможность запустить:
  - baseline без backplane;
  - multi-instance с backplane;
- возможность сравнить два режима на одном и том же проекте.

## 3. Идентификатор экземпляра сервиса

### Зачем нужен

Для защиты нужно явно показывать, что разные клиенты сидят на разных экземплярах сервиса.

### Что лучше сделать

Добавить сервис или конфигурацию, которая даёт `serverInstanceId`.

Источники значения:

- переменная окружения;
- имя контейнера;
- hostname.

### Где использовать

- в логах подключения;
- в логах рассылки событий;
- в debug endpoint или debug hub method;
- в ответах диагностического API, если сделаем такой endpoint.

## 4. Диагностический контур для доказательства

Самая частая ошибка в таких работах: архитектура работает, но доказать это на защите трудно.

### Минимально полезные диагностические данные

- `serverInstanceId`
- `connectionId`
- `groupKey`
- `eventId`
- `entityId`
- `originNode`
- `createdAt`

### Важное решение

Не стоит массово ломать пользовательские socket payload'ы ради метаданных.

Лучше разделить:

- боевые payload'ы оставить совместимыми;
- диагностические поля добавить в логи, трассировку и отдельные debug-представления.

### Где логировать

- в [ReportPageHub.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Hubs/ReportPageHub.cs:1)
- в [ReportPageHubClient.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Hubs/ReportPageHubClient.cs:1)
- при публикации ключевых типов событий

## 5. Диагностический endpoint или hub method

### Зачем нужен

Чтобы из браузера или демонстрационного UI быстро получить:

- идентификатор узла;
- текущий `connectionId`;
- информацию о состоянии соединения.

### Предпочтительный вариант

Небольшой debug endpoint только для ветки ВКР или development-режима.

Пример полезного ответа:

- `serverInstanceId`
- `machineName`
- `environment`
- `signalRConnectionId` при наличии

Второй вариант:

- отдельный метод в хабе для получения debug-информации по соединению.

## 6. Улучшение наблюдаемости на фронте

### Что уже есть

- баннер обрыва соединения;
- повторное подключение;
- повторное вступление в группу отчёта.

### Что имеет смысл добавить

- debug-плашку или debug-панель только для стенда ВКР;
- отображение:
  - текущего `connectionId`;
  - текущего `serverInstanceId`;
  - статуса сокета;
  - возможно номера последнего `eventId`.

### Почему это полезно

- облегчает демонстрацию на защите;
- уменьшает зависимость от чтения серверных логов в реальном времени;
- позволяет делать скриншоты для ВКР.

## 7. Конфигурация nginx для multi-instance

### Основной файл

- [upstreams.conf](/Users/gently/projects/bugreport-root/bugget/nginx/upstreams.conf:1)

### Что нужно изменить

- для стенда ВКР `app-api` должен указывать на несколько экземпляров:
  - `bugget-api-1:7777`
  - `bugget-api-2:7777`

### Что отдельно проверить

- поддержка WebSocket upgrade headers;
- поведение балансировки для нескольких клиентов;
- нужен ли отдельный режим affinity для части сценариев;
- можно ли для стенда обойтись WebSocket-only режимом без жёсткой affinity.

## 8. Режимы испытаний

С точки зрения реализации нужно поддержать три режима:

### Режим A. Single-node baseline

- один `bugget-api`
- без backplane

### Режим B. Multi-instance без backplane

- два `bugget-api`
- без backplane

### Режим C. Multi-instance с backplane

- два `bugget-api`
- с Redis backplane

Именно режим B особенно важен для ВКР, потому что он наглядно показывает существование проблемы.

## 9. Что уже можно использовать без доработки

### Уже полезно

- `withAutomaticReconnect` на фронте;
- повторное `JoinReportGroupAsync` после reconnect;
- существующая модель групп по report context;
- передача `X-Signal-R-Connection-Id` из frontend API-запросов.

### Что это означает

Не нужно выдумывать архитектуру с нуля. Работа может быть честно оформлена как развитие уже существующего real-time контура до multi-instance режима.

## 10. Что стоит сделать отдельными артефактами внутри репозитория ВКР

После начала реализации стоит завести:

- `materials/test-scenarios.md`
- `materials/metrics-plan.md`
- `materials/architecture-as-is.md`
- `materials/architecture-to-be.md`
- `materials/03-proof-stand/runbook-thesis-stand.md`

## 11. Рекомендуемый порядок реализации

1. Завести отдельную ветку под ВКР.
2. Подготовить отдельный compose-стенд для multi-instance режима.
3. Подключить Redis backplane в backend.
4. Добавить `serverInstanceId` и диагностическое логирование.
5. Подготовить debug-способ показать узел и соединение на фронте.
6. Прогнать baseline, broken multi-instance и fixed multi-instance сценарии.
7. Только после этого формализовать программу испытаний и собирать таблицы результатов.

## 12. Главный инженерный принцип

Для ВКР выгоднее минимально вторгаться в существующие бизнес-payload'ы и максимально усиливать:

- инфраструктурную воспроизводимость;
- наблюдаемость;
- экспериментальную проверяемость;
- наглядность доказательства межузловой доставки.
