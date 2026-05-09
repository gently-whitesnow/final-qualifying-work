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
cd /Users/gently/projects/bugreport-root/bugget
node scripts/realtime-scaleout-check.mjs
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
  }
}
```

Интерпретация:

- клиент A был подключен к `app-api-1`;
- клиент B был подключен к `app-api-2`;
- событие изменения отчета, созданное через первый узел, было доставлено клиенту на втором узле;
- межузловая доставка через Redis backplane подтверждена.

## Результат без Redis backplane

Стенд запущен командой:

```bash
docker compose -f docker-compose.thesis.yml -f docker-compose.thesis.no-backplane.yml up -d --build
```

Результат:

```text
Error: ReceiveReportPatch timed out after 10000ms
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
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml config --quiet
docker compose -f docker-compose.thesis.yml -f docker-compose.thesis.no-backplane.yml config --quiet
docker exec nginx_app_thesis nginx -t
```

Результаты:

- обе compose-конфигурации валидны;
- `nginx -t` подтверждает корректность конфигурации;
- автоматизированный сценарий real-time smoke воспроизводит отличие между режимами с backplane и без него.

## Вывод

Эксперимент подтверждает ключевой тезис ВКР: single-node ограничение real-time контура устраняется при переходе к архитектуре с несколькими экземплярами `app-api` и Redis backplane. В режиме без backplane воспроизводится фрагментация real-time пространства, а в режиме с backplane одно и то же событие доставляется клиенту, подключенному к другому серверному экземпляру.
