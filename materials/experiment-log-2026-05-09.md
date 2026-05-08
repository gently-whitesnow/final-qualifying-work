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

## Проверка UI-стенда через nginx

Фронтенд запущен командой:

```bash
cd /Users/gently/projects/bugreport-root/bugget/frontend
VITE_SIGNALR_SKIP_NEGOTIATION=true npm run dev -- --host 0.0.0.0
```

Проверки входной точки:

```bash
curl -sS -D - http://localhost:18080/ -o /tmp/bugget-thesis-root.html
curl -sS -D - http://localhost:18080/login -o /tmp/bugget-thesis-login.html
curl -sS -D - http://localhost:18080/@vite/client -o /tmp/bugget-thesis-vite-client.js
curl -sS -D - http://localhost:18080/src/app/main.tsx -o /tmp/bugget-thesis-app-main.tsx
curl -sS -D - http://localhost:18080/env.js -o /tmp/bugget-thesis-env.js
```

Результат:

- `http://localhost:18080/` возвращает `302` с относительным `Location: /login?next=/`;
- `http://localhost:18080/login` возвращает `200 OK` и HTML frontend-приложения;
- `http://localhost:18080/@vite/client` возвращает `200 OK` и `Content-Type: text/javascript`;
- `http://localhost:18080/src/app/main.tsx` возвращает `200 OK` и `Content-Type: text/javascript`;
- `http://localhost:18080/env.js` возвращает `200 OK` и runtime-конфигурацию self-hosted режима.

Интерпретация:

- демонстрационный UI доступен через единый nginx-вход `http://localhost:18080`;
- порт `18080` больше не теряется при auth-редиректе;
- dev-ресурсы Vite и runtime-конфигурация доступны без ручных обходов, поэтому стенд подходит для скриншотов и демонстрации real-time debug-badge.

## Повторная проверка после настройки UI

Проверки:

```bash
cd /Users/gently/projects/bugreport-root/bugget
docker compose -f docker-compose.thesis.yml config --quiet
docker exec nginx_bugget_thesis nginx -t

cd /Users/gently/projects/bugreport-root/bugget/frontend
npm run build
npm run test:realtime-scaleout
```

Результаты:

- `docker compose ... config --quiet` завершился без ошибок;
- `nginx -t` подтвердил корректность конфигурации;
- `npm run build` завершился успешно;
- `npm run test:realtime-scaleout` завершился успешно.

Повторный результат real-time smoke:

```json
{
  "ok": true,
  "reportId": "8",
  "patchedTitle": "scaleout-patched-1778276339113",
  "nodeA": {
    "serverInstanceId": "bugget-api-1",
    "machineName": "855bc0100a30",
    "connectionId": "vmXX43lNLIi_llZ_Pi9asg",
    "userIdentifier": "thesis-user"
  },
  "nodeB": {
    "serverInstanceId": "bugget-api-2",
    "machineName": "5cdcd6f5f7be",
    "connectionId": "G-ckoeAvaOk-h3KnIQkBgw",
    "userIdentifier": "thesis-user"
  },
  "receivedPatch": {
    "title": "scaleout-patched-1778276339113",
    "updatedAt": "2026-05-08T21:38:59.475596+00:00"
  }
}
```
