**Вывод**

Запрос сильный и реалистичный. `bugget` уже содержит рабочую real-time основу, поэтому ВКР можно строить не как “новую систему с нуля”, а как инженерный апгрейд существующего продукта: переход от локального single-node WebSocket-решения к распределённому real-time интерфейсу с поддержкой горизонтального масштабирования.

Это подтверждается кодом:
- проект позиционируется как платформа для работы с баг-репортами: [README.md](/Users/gently/projects/bugreport-root/bugget/README.md:3)
- в бэкенде уже есть `SignalR`-хаб и endpoint `/v1/report-page-hub`: [ServiceCollectionExtensions.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Extensions/ServiceCollectionExtensions.cs:110), [ApplicationBuilderExtensions.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Extensions/ApplicationBuilderExtensions.cs:21)
- сообщения идут по группам репорта, то есть модель совместной работы уже намечена: [ReportPageHub.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Hubs/ReportPageHub.cs:15), [ReportPageHubClient.cs](/Users/gently/projects/bugreport-root/bugget/backend/bugget-api/Bugget/Hubs/ReportPageHubClient.cs:15)
- на фронте уже есть WebSocket-only подключение, автопереподключение и баннер деградации: [connection.ts](/Users/gently/projects/bugreport-root/bugget/frontend/src/shared/model/socket/connection.ts:18), [SystemBanner.tsx](/Users/gently/projects/bugreport-root/bugget/frontend/src/shared/ui/notifications/SystemBanner.tsx:32)
- событий много, значит real-time слой уже влияет на UX, а не существует “для галочки”: [contracts.ts](/Users/gently/projects/bugreport-root/bugget/frontend/src/shared/model/socket/contracts.ts:81)

**Что важно уточнить в формулировке**

Самый рискованный момент в вашем запросе: термин `децентрализованные веб-сокеты`.

Для ВКР я бы его не делал центральным. Причина простая: и ваш текущий стек, и подход Figma, и типовой `SignalR scale-out` — это не децентрализация в смысле P2P/federation, а распределённая централизованная архитектура. У Figma в статье от `16 октября 2019` прямо описан client/server cluster over WebSockets, где сервер задаёт порядок событий. То есть вдохновляться Figma полезно, но именно как пример распределённого multiplayer, а не децентрализации.

Поэтому лучше опираться на такие формулировки:
- `распределённый real-time слой`
- `масштабируемая WebSocket-подсистема`
- `подсистема синхронизации между экземплярами сервиса`
- `real-time интерфейс с поддержкой горизонтального масштабирования`

**Насколько тема ВКР совпадает с проектом**

Тема `"Разработка real-time интерфейса с поддержкой горизонтального масштабирования WebSocket-соединений для системы отслеживания задач"` в целом подходит, но есть нюанс: сам `bugget` у вас описан как система работы с баг-репортами, а не абстрактная task-tracking система.

Это не критично. Есть два пути:
- Если название можно немного править, точнее будет что-то вроде: `...для системы отслеживания задач и баг-репортов` или `...для системы обработки баг-репортов`.
- Если название уже фиксировано, в пояснительной записке стоит явно показать, что баг-репорт в `bugget` выступает как единица совместной работы: у него есть статус, ответственный, комментарии, вложения, шаги воспроизведения, ссылки. То есть по сути это task-like сущность.

**Что должно стать содержанием ВКР**

Чтобы работа соответствовала названию, апгрейд лучше строить не вокруг “просто добавить сокеты”, а вокруг масштабирования real-time контура:
- вынести доставку SignalR-событий из single-instance режима в межузловую синхронизацию
- добавить `Redis backplane` или другой broker между несколькими экземплярами `bugget-api`
- поднять 2-3 инстанса `bugget-api` за балансировщиком вместо одного upstream: сейчас upstream один, [upstreams.conf](/Users/gently/projects/bugreport-root/bugget/nginx/upstreams.conf:9)
- учесть sticky sessions/session affinity: Microsoft для scale-out SignalR это отдельно подчёркивает
- измерить задержку доставки, стабильность переподключения, доставку событий между разными нодами, поведение при падении инстанса
- усилить UX real-time режима: presence, индикация активных участников, статус синхронизации, деградированный режим

**Что брать у Figma, а что не брать**

Из статьи Figma стоит взять идеи:
- документ-центричная модель: у вас это уже естественно ложится на “страницу репорта”
- мелкие patch-события вместо полной пересылки состояния
- простая модель reconnect: клиент восстанавливает актуальное состояние и продолжает синхронизацию
- сначала прототип и сценарии конкурирующих изменений, потом интеграция в основной код

Не стоит брать как тезис:
- `децентрализацию`
- полный CRDT/OT как обязательную часть ВКР

Для вашей темы достаточно значительно более прагматичного уровня: надёжная межузловая доставка WebSocket-событий, согласованность UI и устойчивость при scale-out.

**Итог**

В текущем виде запрос хорошо ложится на ВКР, если позиционировать её так: не “я взял старый pet-проект и чуть его допилил”, а “я разработал и исследовал распределённый real-time контур для совместной работы над сущностями системы, устранив ограничение single-node WebSocket-архитектуры”.

Источники:
- [How Figma’s multiplayer technology works](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)
- [ASP.NET Core SignalR hosting and scaling](https://learn.microsoft.com/en-us/aspnet/core/signalr/scale?view=aspnetcore-10.0)
