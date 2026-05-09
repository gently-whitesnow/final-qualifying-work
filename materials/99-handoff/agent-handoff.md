# Контекст для следующего агента

## Основные пути

- Рабочий репозиторий ВКР и практики: `/Users/gently/projects/final-qualifying-work`
- Целевой проект для анализа и доработки: `/Users/gently/projects/bugreport-root/bugget/backend/bugget-api`
- Связанный корневой репозиторий продукта: `/Users/gently/projects/bugreport-root/bugget`

## Ключевые материалы

- Общий контекст и тема: `/Users/gently/projects/final-qualifying-work/README.md`
- Вопросы и ответы по индивидуальному заданию: `/Users/gently/projects/final-qualifying-work/materials/01-research/questions.md`
- Предварительное техническое исследование: `/Users/gently/projects/final-qualifying-work/materials/01-research/code-research.md`
- Наброски по структуре и ограничениям: `/Users/gently/projects/final-qualifying-work/materials/01-research/insights.md`
- Методические требования по практике: `/Users/gently/projects/final-qualifying-work/materials/00-source-documents/Практика2026заочное.pdf`
- Учебно-методическое пособие по отчетам: `/Users/gently/projects/final-qualifying-work/materials/00-source-documents/Программная_инженерия._Требования_к_подготовке_и_содержанию_отчетов_по_практике.pdf`
- Шаблон индивидуального задания: `/Users/gently/projects/final-qualifying-work/materials/00-source-documents/ИндивидуальноеЗадание2026заоч.docx`
- Шаблон титульного листа отчета: `/Users/gently/projects/final-qualifying-work/materials/00-source-documents/ТитульныйЛист2026заочное.docx`
- Шаблон презентации по практике: `/Users/gently/projects/final-qualifying-work/materials/00-source-documents/ШаблонПДП2026.pptx`
- Черновик содержательной части ВКР: `/Users/gently/projects/final-qualifying-work/materials/04-docx/vkr-draft-content.md`

## Утвержденная тема

`Разработка real-time интерфейса с поддержкой горизонтального масштабирования WebSocket-соединений для системы отслеживания задач`

Тему менять не нужно: она соответствует приказу и намеренно избегает англицизмов.

## Что уже подтверждено

- Практика проходит в институте.
- Руководитель: Сергей Александрович Рогачев, старший преподаватель.
- За практику планируется закрыть максимум работы по ВКР, а не только формальный отчет.
- Основной целевой документ: сразу полная ВКР; отчет по практике потом извлекается из нее.
- Реальная доработка проекта является доказательной базой работы.
- Разработку нужно вести в отдельной ветке, без мержей в `main`; ветка нужна именно под ВКР.
- Для доказательства результата достаточно минимального, но убедительного стенда.
- Можно использовать весь репозиторий `/Users/gently/projects/bugreport-root/bugget`, включая `nginx` и `docker-compose`. Полноценный пользовательский интерфейс не нужно включать в доказательный контур ВКР: достаточно минимального проверочного клиента.
- Примеры из `examples.zip` разрешено распаковать и использовать как ориентир по структуре.

## Ключевые технические наблюдения

- В backend-коде целевой системы уже есть SignalR-хаб `ReportPageHub` и endpoint `/v1/report-page-hub`.
- Real-time события отправляются в групповые каналы по контексту репорта через `ReportPageHubClient`.
- В базовом `nginx`-контуре upstream `app-api` указывает на один экземпляр backend-сервиса, что подтверждает single-node ограничение.
- В корневом `docker-compose.yml` уже есть Redis, поэтому тема горизонтального масштабирования через межузловую синхронизацию выглядит естественной и проверяемой.

## Ожидаемый конвейер работы

1. Сформировать сильный промпт для внешнего глубокого исследования подходов, архитектур и доказательной базы.
2. Положить результаты исследования в этот репозиторий.
3. На основе исследования и кода сформировать полную ВКР.
4. Из полной ВКР извлечь отчет по практике.
5. Собрать `.docx` через MCP-инструменты.
6. Привести документ к требованиям ГОСТ и шаблонов.
7. Подготовить презентацию для защиты.

## Защитимый тезис

`я разработал и исследовал распределённый real-time контур для совместной работы над сущностями системы, устранив ограничение single-node WebSocket-архитектуры`

Этот тезис нужно натягивать на утвержденную тему, не меняя ее формулировку.

## Что особенно важно доказать

- Личный вклад выражен не только в описании идеи, но и в реальной изолированной реализации в отдельной ветке.
- До доработки система имела ограничение single-node для real-time взаимодействия.
- После доработки появился работоспособный масштабируемый контур межузловой доставки событий.
- Результат подтвержден не только кодом, но и испытаниями:
  - функциональными сценариями cross-node delivery;
  - сценариями отказа и переподключения;
  - базовыми метриками или нагрузочным экспериментом;
  - воспроизводимым стендом на минимальной инфраструктуре.

## Текущий статус реализации

- Рабочая ветка продукта: `thesis/realtime-scaleout`.
- Стенд с Redis backplane запускается через `/Users/gently/projects/bugreport-root/bugget/docker-compose.thesis.yml`.
- Режим без backplane запускается через комбинацию `/Users/gently/projects/bugreport-root/bugget/docker-compose.thesis.yml` и `/Users/gently/projects/bugreport-root/bugget/docker-compose.thesis.no-backplane.yml`.
- Для thesis-стенда добавлен отдельный nginx-конфиг `/Users/gently/projects/bugreport-root/bugget/nginx/nginx.thesis.conf`, который проксирует HTTP/WebSocket-трафик на upstream `app-api` и не зависит от дополнительных продуктовых сервисов.
- Сервисы стенда в compose названы `app-api-1`, `app-api-2`, `redis_app_thesis`, `postgres_app_thesis`, `nginx_app_thesis`.
- Минимальный проверочный клиент находится в `/Users/gently/projects/bugreport-root/bugget/scripts/realtime-scaleout-check.mjs`.
- Автоматизированный сценарий `node scripts/realtime-scaleout-check.mjs` или `npm run test:realtime-scaleout` подтвердил доставку события между `app-api-1` и `app-api-2` при включенном Redis backplane.
- Проверочный клиент расширен серийным режимом `THESIS_ITERATIONS=N`; короткий прогон `THESIS_ITERATIONS=5 node scripts/realtime-scaleout-check.mjs` дал 5 успешных доставок из 5, `avg = 5,5 мс`, `p50 = 4,4 мс`, `p95 = 9,5 мс`.
- При отключенном backplane тот же сценарий завершался timeout, что фиксирует исходное ограничение multi-instance режима.

## Важные ограничения по оформлению

- Для отчета по преддипломной практике рекомендуется объем 25-35 страниц.
- Для содержательной части полной ВКР ориентир из заметок: 40-60 страниц.
- Источников должно быть не менее 15.
- Интернет-источники: не более 50 процентов списка.
- Иностранные источники: желательно, но не более 50 процентов списка.
- Базовое оформление: Times New Roman, 14 pt, полуторный интервал, ГОСТ 7.32-2017, список источников по ГОСТ 7.0.100-2018.

## Текущий статус DOCX

- Актуальный DOCX: `/Users/gently/projects/final-qualifying-work/build/docx/vkr-draft-1.docx`.
- Генератор DOCX: `/Users/gently/projects/final-qualifying-work/scripts/build_vkr_docx.py`.
- Рендер для визуальной проверки: `/Users/gently/projects/final-qualifying-work/build/docx/rendered`.
- В генератор добавлены три воспроизводимые иллюстрации: single-node архитектура, multi-instance архитектура с Redis backplane, поток события `ReceiveReportPatch`.
- Титульный лист помещается на одну страницу, содержание статическое и синхронизировано с текущим render-проходом.
- В актуальном DOCX нет старых маркеров `authorization-api`, `users-api`, `bugget-api-1`, `bugget-api-2`, `frontend`, `RealtimeDebugBadge`.
