# Лог эксперимента 2026-05-09

## Контекст

Ветка проекта:

`thesis/realtime-scaleout`

Стенд:

- `app-api-1`;
- `app-api-2`;
- `redis_app_thesis`;
- `postgres_app_thesis`;
- `nginx_app_thesis`.

Проверочный сценарий:

1. Создать отчет через `app-api-1`.
2. Подключить SignalR-клиент A к `app-api-1`.
3. Подключить SignalR-клиент B к `app-api-2`.
4. Подписать оба клиента на группу отчета.
5. Изменить заголовок отчета через `app-api-1`.
6. Проверить, получил ли клиент B событие `ReceiveReportPatch`.

Команда:

```bash
cd /Users/gently/projects/bugget-fqw
node scripts/realtime-scaleout-check.mjs
```

Для серийной проверки:

```bash
cd /Users/gently/projects/bugget-fqw
THESIS_ITERATIONS=5 node scripts/realtime-scaleout-check.mjs
```

Для проверки восстановления:

```bash
THESIS_SCENARIO=rejoin node scripts/realtime-scaleout-check.mjs
THESIS_SCENARIO=failover THESIS_ALLOW_DOCKER_CONTROL=1 THESIS_TIMEOUT_MS=20000 node scripts/realtime-scaleout-check.mjs
```

## Результат с Redis backplane

Стенд запущен командой:

```bash
docker compose -f docker-compose.thesis.yml up -d --build
```

Результат:

```json
{
  "ok": true,
  "reportId": "3",
  "patchedTitle": "scaleout-patched-1778316874715",
  "nodeA": {
    "serverInstanceId": "app-api-1",
    "machineName": "21ee5de48b13",
    "connectionId": "9iIIs9uWgfJlf6BHXER8XA",
    "userIdentifier": "thesis-user"
  },
  "nodeB": {
    "serverInstanceId": "app-api-2",
    "machineName": "1d6a8589cdae",
    "connectionId": "NpH7DSAYYJW1EWM2XKhyqQ",
    "userIdentifier": "thesis-user"
  },
  "receivedPatch": {
    "title": "scaleout-patched-1778316874715",
    "updatedAt": "2026-05-09T08:54:35.186614+00:00"
  },
  "metrics": {
    "deliveryLatencyMs": 9.5,
    "patchRequestMs": 8.5
  }
}
```

Интерпретация:

- клиент A был подключен к `app-api-1`;
- клиент B был подключен к `app-api-2`;
- событие изменения отчета, созданное через первый узел, было доставлено клиенту на втором узле;
- межузловая доставка через Redis backplane подтверждена.

## Серийная проверка с Redis backplane

Команда:

```bash
THESIS_ITERATIONS=5 node scripts/realtime-scaleout-check.mjs
```

Результат:

```json
{
  "ok": true,
  "iterations": 5,
  "successful": 5,
  "failed": 0,
  "latencyMs": {
    "min": 5.5,
    "max": 11.6,
    "avg": 8.4,
    "p50": 9.1,
    "p95": 11.6
  }
}
```

Интерпретация:

- все 5 проверок подтвердили доставку события между `app-api-1` и `app-api-2`;
- средняя задержка доставки в локальном стенде составила 8,4 мс;
- p50 составил 9,1 мс, p95 составил 11,6 мс;
- результат не является полноценным нагрузочным тестом, но подтверждает повторяемость ключевого свойства на короткой серии запусков.

## Дополнительная серийная проверка 2026-05-23

Команда:

```bash
cd /Users/gently/projects/bugget-fqw
THESIS_ITERATIONS=30 node scripts/realtime-scaleout-check.mjs
```

Результат:

```json
{
  "ok": true,
  "iterations": 30,
  "successful": 30,
  "failed": 0,
  "latencyMs": {
    "min": 3.8,
    "max": 16.7,
    "avg": 7.2,
    "p50": 6.1,
    "p95": 13.8
  }
}
```

Интерпретация:

- все 30 проверок подтвердили доставку события между `app-api-1` и `app-api-2`;
- средняя задержка доставки в локальном стенде составила 7,2 мс;
- p50 составил 6,1 мс, p95 составил 13,8 мс;
- расширенная серия усиливает доказательную базу по сравнению с первичной серией из 5 итераций.

## Проверка повторного вступления в группу

Команда:

```bash
THESIS_SCENARIO=rejoin node scripts/realtime-scaleout-check.mjs
```

Результат:

```json
{
  "ok": true,
  "scenario": "rejoin",
  "nodeBInitial": {
    "serverInstanceId": "app-api-2",
    "connectionId": "q7EhgNR3gkZ-r1WQDYQZwg"
  },
  "nodeBRecovered": {
    "serverInstanceId": "app-api-2",
    "connectionId": "C9L4om67BGOZwG8zwEQHxg"
  },
  "metrics": {
    "reconnectAndRejoinMs": 12.9,
    "secondDeliveryLatencyMs": 6.6
  }
}
```

Интерпретация:

- после разрыва клиент получил новый `connectionId`;
- клиент повторно вступил в группу отчета;
- последующее событие `ReceiveReportPatch` было доставлено после повторной подписки.

Повторная проверка 2026-05-23:

```json
{
  "ok": true,
  "scenario": "rejoin",
  "metrics": {
    "firstDeliveryLatencyMs": 5.0,
    "reconnectAndRejoinMs": 6.5,
    "secondDeliveryLatencyMs": 15.2
  }
}
```

## Проверка отказа одного узла

Команда:

```bash
THESIS_SCENARIO=failover THESIS_ALLOW_DOCKER_CONTROL=1 THESIS_TIMEOUT_MS=20000 node scripts/realtime-scaleout-check.mjs
```

Результат:

```json
{
  "ok": true,
  "scenario": "failover",
  "stoppedContainer": "app-api-2",
  "nodeBBeforeFailure": {
    "serverInstanceId": "app-api-2",
    "connectionId": "shWDsU7gAMAt0DMhTlpKmw"
  },
  "nodeBAfterFailover": {
    "serverInstanceId": "app-api-1",
    "connectionId": "jTO0YR68SSaLbtrtxLsq-w"
  },
  "metrics": {
    "failoverReconnectAndRejoinMs": 240.3,
    "secondDeliveryLatencyMs": 7.3
  }
}
```

Интерпретация:

- клиент был подключен через nginx к `app-api-2`;
- после остановки `app-api-2` клиент переподключился к `app-api-1`;
- после повторного вступления в группу клиент получил новое событие;
- режим подтверждает восстановление real-time контура при отказе одного экземпляра `app-api`.

Повторная проверка 2026-05-23:

```json
{
  "ok": true,
  "scenario": "failover",
  "nodeBBeforeFailure": {
    "serverInstanceId": "app-api-2"
  },
  "nodeBAfterFailover": {
    "serverInstanceId": "app-api-1"
  },
  "metrics": {
    "firstDeliveryLatencyMs": 7.8,
    "failoverReconnectAndRejoinMs": 352.0,
    "secondDeliveryLatencyMs": 5.4
  }
}
```

## Результат без Redis backplane

Стенд запущен командой:

```bash
docker compose -f docker-compose.thesis.yml -f docker-compose.thesis.no-backplane.yml up -d --build
```

Результат:

```text
Error: ReceiveReportPatch timed out after 10000ms
```

Повторная проверка 2026-05-23 с укороченным таймаутом:

```bash
THESIS_TIMEOUT_MS=4000 node scripts/realtime-scaleout-check.mjs
```

```text
Error: ReceiveReportPatch timed out after 4000ms
```

Интерпретация:

- клиент A был подключен к одному экземпляру сервиса;
- клиент B был подключен к другому экземпляру сервиса;
- при отключенном backplane событие не было доставлено между узлами;
- это подтверждает исходное ограничение multi-instance режима без межузловой синхронизации.

## Проверка входной точки nginx

Проверка:

```bash
curl -sS http://localhost:18080/health
```

Результат:

```text
ok
```

Интерпретация:

- стенд имеет единую входную точку nginx;
- nginx-конфигурация не зависит от дополнительных сервисов и проксирует HTTP/WebSocket-трафик на upstream `app-api`;
- полноценный пользовательский интерфейс не входит в доказательный контур ВКР.

## Проверки конфигурации

```bash
cd /Users/gently/projects/bugget-fqw
docker compose -f docker-compose.thesis.yml config --quiet
docker compose -f docker-compose.thesis.yml -f docker-compose.thesis.no-backplane.yml config --quiet
docker exec nginx_app_thesis nginx -t
```

Результаты:

- обе compose-конфигурации валидны;
- `nginx -t` подтверждает корректность конфигурации;
- автоматизированный сценарий real-time smoke воспроизводит отличие между режимами с backplane и без него;
- серийный режим `THESIS_ITERATIONS=30` подтверждает повторяемость результата и собирает первичные метрики задержки;
- режимы `THESIS_SCENARIO=rejoin` и `THESIS_SCENARIO=failover` подтверждают восстановление подписки после разрыва и остановки одного узла.

## Вывод

Эксперимент подтверждает ключевой тезис ВКР: single-node ограничение real-time контура устраняется при переходе к архитектуре с несколькими экземплярами `app-api` и Redis backplane. В режиме без backplane воспроизводится фрагментация real-time пространства, а в режиме с backplane одно и то же событие доставляется клиенту, подключенному к другому серверному экземпляру. Серийный запуск из 30 итераций дополнительно показал повторяемость результата и дал первичную оценку задержки доставки. Rejoin- и failover-сценарии подтвердили, что клиент может восстановить рабочую подписку после разрыва соединения и остановки одного узла.
