# Лог эксперимента 2026-05-09

## Контекст

Ветка проекта:

`thesis/realtime-scaleout`

Стенд:

- `bugget-api-1`
- `bugget-api-2`
- `redis`
- `postgres`
- `nginx`

Проверочный сценарий:

1. Создать отчет через `bugget-api-1`.
2. Подключить SignalR-клиент A к `bugget-api-1`.
3. Подключить SignalR-клиент B к `bugget-api-2`.
4. Подписать оба клиента на группу отчета.
5. Изменить заголовок отчета через `bugget-api-1`.
6. Проверить, получил ли клиент B событие `ReceiveReportPatch`.

Команда:

```bash
cd /Users/gently/projects/bugreport-root/bugget/frontend
npm run test:realtime-scaleout
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
  "reportId": "7",
  "patchedTitle": "scaleout-patched-1778275880780",
  "nodeA": {
    "serverInstanceId": "bugget-api-1",
    "machineName": "855bc0100a30",
    "connectionId": "8dxLm6-cGHYFV3_nTPFazQ",
    "userIdentifier": "thesis-user"
  },
  "nodeB": {
    "serverInstanceId": "bugget-api-2",
    "machineName": "5cdcd6f5f7be",
    "connectionId": "QDJgmgUiQy023cWXSpZ3DQ",
    "userIdentifier": "thesis-user"
  },
  "receivedPatch": {
    "title": "scaleout-patched-1778275880780",
    "updatedAt": "2026-05-08T21:31:21.185315+00:00"
  }
}
```

Интерпретация:

- клиент A был подключен к `bugget-api-1`;
- клиент B был подключен к `bugget-api-2`;
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

## Вывод

Эксперимент подтверждает ключевой тезис ВКР: single-node ограничение real-time контура устраняется при переходе к архитектуре с несколькими экземплярами `bugget-api` и Redis backplane. В режиме без backplane воспроизводится фрагментация real-time пространства, а в режиме с backplane одно и то же событие доставляется клиенту, подключенному к другому серверному экземпляру.

