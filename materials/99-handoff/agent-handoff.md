# Контекст для следующего агента

## Основные пути

- Рабочий репозиторий ВКР и практики: `/Users/gently/projects/final-qualifying-work`
- Целевой проект для анализа и доработки: `/Users/gently/projects/bugget-fqw/backend/bugget-api`
- Связанный корневой репозиторий продукта: `/Users/gently/projects/bugget-fqw`

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
- Научный руководитель ВКР: Фомин Александр Владимирович, канд. техн. наук, доцент.
- Руководитель практики: Сергей Александрович Рогачев, старший преподаватель.
- За практику планируется закрыть максимум работы по ВКР, а не только формальный отчет.
- Основной целевой документ: сразу полная ВКР; отчет по практике потом извлекается из нее.
- Реальная доработка проекта является доказательной базой работы.
- Разработку нужно вести в отдельной ветке, без мержей в `main`; ветка нужна именно под ВКР.
- Для доказательства результата достаточно минимального, но убедительного стенда.
- Можно использовать весь репозиторий `/Users/gently/projects/bugget-fqw`, включая `nginx` и `docker-compose`. Полноценный пользовательский интерфейс не нужно включать в доказательный контур ВКР: достаточно минимального проверочного клиента.
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
- Стенд с Redis backplane запускается через `/Users/gently/projects/bugget-fqw/docker-compose.thesis.yml`.
- Режим без backplane запускается через комбинацию `/Users/gently/projects/bugget-fqw/docker-compose.thesis.yml` и `/Users/gently/projects/bugget-fqw/docker-compose.thesis.no-backplane.yml`.
- Для thesis-стенда добавлен отдельный nginx-конфиг `/Users/gently/projects/bugget-fqw/nginx/nginx.thesis.conf`, который проксирует HTTP/WebSocket-трафик на upstream `app-api` и не зависит от дополнительных продуктовых сервисов.
- Сервисы стенда в compose названы `app-api-1`, `app-api-2`, `redis_app_thesis`, `postgres_app_thesis`, `nginx_app_thesis`.
- Минимальный проверочный клиент находится в `/Users/gently/projects/bugget-fqw/scripts/realtime-scaleout-check.mjs`.
- Автоматизированный сценарий `node scripts/realtime-scaleout-check.mjs` или `npm run test:realtime-scaleout` подтвердил доставку события между `app-api-1` и `app-api-2` при включенном Redis backplane.
- Проверочный клиент расширен серийным режимом `THESIS_ITERATIONS=N`; прогон `THESIS_ITERATIONS=30 node scripts/realtime-scaleout-check.mjs` от 23.05.2026 дал 30 успешных доставок из 30, `avg = 7,2 мс`, `p50 = 6,1 мс`, `p95 = 13,8 мс`.
- Режим `THESIS_SCENARIO=rejoin` подтвердил повторное вступление клиента в группу после разрыва соединения: новый `connectionId`, последующее событие получено, `reconnectAndRejoinMs = 6,5 мс`.
- Режим `THESIS_SCENARIO=failover THESIS_ALLOW_DOCKER_CONTROL=1 THESIS_TIMEOUT_MS=20000` подтвердил восстановление после остановки `app-api-2`: клиент через nginx перешел с `app-api-2` на `app-api-1`, повторно вступил в группу и получил событие; `failoverReconnectAndRejoinMs = 352,0 мс`.
- При отключенном backplane тот же сценарий завершался timeout, что фиксирует исходное ограничение multi-instance режима.

## Важные ограничения по оформлению

- Для отчета по преддипломной практике рекомендуется объем 25-35 страниц.
- Для текущего универсального варианта ВКР/отчета по практике пользователь попросил целиться в 35 страниц, чтобы документ подходил и для отчета по практике, и как база будущего итогового ВКР.
- Источников должно быть не менее 15.
- Интернет-источники: не более 50 процентов списка.
- Иностранные источники: желательно, но не более 50 процентов списка.
- Базовое оформление: Times New Roman, 14 pt, полуторный интервал, ГОСТ 7.32-2017, список источников по ГОСТ 7.0.100-2018.

## Текущий статус DOCX

- Актуальный DOCX: `/Users/gently/projects/final-qualifying-work/build/docx/vkr-draft-1.docx`.
- Отдельная версия отчета по преддипломной практике: `/Users/gently/projects/final-qualifying-work/build/docx/practice-report-draft-1.docx`.
- План дальнейшего улучшения ВКР: `/Users/gently/projects/final-qualifying-work/materials/02-planning/further-vkr-improvement-plan.md`.
- Генератор DOCX: `/Users/gently/projects/final-qualifying-work/scripts/build_vkr_docx.py`.
- Генератор отчета по практике: `/Users/gently/projects/final-qualifying-work/scripts/build_practice_report_docx.py`.
- Рендер для визуальной проверки: `/Users/gently/projects/final-qualifying-work/build/docx/rendered`.
- В генератор добавлены три воспроизводимые иллюстрации: single-node архитектура, multi-instance архитектура с Redis backplane, поток события `ReceiveReportPatch`.
- Титульный лист помещается на одну страницу, содержание статическое и синхронизировано с текущим render-проходом.
- Актуальный DOCX после удаления спорных добавок занимает 37 страниц. Версия отчета по практике после добавления подраздела с описанием литературы занимает 35 страниц и остается в рекомендованном диапазоне 25-35 страниц.
- В актуальном DOCX нет старых маркеров `authorization-api`, `users-api`, `bugget-api-1`, `bugget-api-2`, `frontend`, `RealtimeDebugBadge`.
- Список источников расширен до 20 наименований: интернет-источники составляют 10 из 20, что соответствует ограничению не более 50 процентов.

## Текущий статус PPTX

- Черновик презентации: `/Users/gently/projects/final-qualifying-work/build/pptx/vkr-defense-draft.pptx`.
- Генератор презентации: `/Users/gently/projects/final-qualifying-work/scripts/build_vkr_pptx.py`.
- Презентация содержит 10 слайдов: проблема, целевая архитектура, реализация, стенд, baseline/backplane, серия, rejoin/failover, практическая значимость и вывод.
- PPTX проверен через LibreOffice export в PDF; временные preview/contact-sheet артефакты удалены, оставлен только финальный `.pptx`.
