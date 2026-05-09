# ВКР: real-time интерфейс и масштабирование WebSocket-соединений

Репозиторий хранит материалы, план, доказательную базу и воспроизводимую сборку DOCX для ВКР.

## Тема

«Разработка real-time интерфейса с поддержкой горизонтального масштабирования WebSocket-соединений для системы отслеживания задач».

## Рабочий тезис

Разработан и исследован распределенный real-time контур для совместной работы над сущностями системы, устраняющий ограничение single-node WebSocket-архитектуры.

## Основные пути

- Репозиторий ВКР: `/Users/gently/projects/final-qualifying-work`
- Целевой проект: `/Users/gently/projects/bugreport-root/bugget`
- Ветка разработки в целевом проекте: `thesis/realtime-scaleout`
- Backend целевого проекта: `/Users/gently/projects/bugreport-root/bugget/backend/bugget-api`

## Структура

- `materials/00-source-documents/` — исходные методички, шаблоны, примеры и архивы.
- `materials/01-research/` — анализ, вопросы, deep-research промпты и заметки по примерам.
- `materials/02-planning/` — планы реализации, спецификация изменений, стратегия доказательства.
- `materials/03-proof-stand/` — runbook стенда и лог эксперимента.
- `materials/04-docx/` — источник текста ВКР и pipeline сборки DOCX.
- `materials/99-handoff/` — контекст для следующего агента.
- `scripts/` — воспроизводимые генераторы.
- `build/docx/` — собранный DOCX, сгенерированные иллюстрации и render-QA.

## Актуальные артефакты

- Черновик ВКР: `build/docx/vkr-draft-1.docx`
- Отчет по преддипломной практике: `build/docx/practice-report-draft-1.docx`
- Черновик презентации: `build/pptx/vkr-defense-draft.pptx`
- Источник контента: `materials/04-docx/vkr-draft-content.md`
- Генератор DOCX: `scripts/build_vkr_docx.py`
- Генератор отчета по практике: `scripts/build_practice_report_docx.py`
- Генератор PPTX: `scripts/build_vkr_pptx.py`
- Pipeline DOCX: `materials/04-docx/docx-pipeline.md`
- Handoff: `materials/99-handoff/agent-handoff.md`

## Сборка DOCX

```bash
cd /Users/gently/projects/final-qualifying-work
/Users/gently/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/build_vkr_docx.py
```

## Сборка отчета по практике

```bash
cd /Users/gently/projects/final-qualifying-work
/Users/gently/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/build_practice_report_docx.py
```

## Render-QA

```bash
cd /Users/gently/projects/final-qualifying-work
env TMPDIR=/private/tmp /Users/gently/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  /Users/gently/.codex/plugins/cache/openai-primary-runtime/documents/26.506.11943/skills/documents/render_docx.py \
  build/docx/vkr-draft-1.docx \
  --output_dir build/docx/rendered \
  --emit_pdf
```

Правило проекта: править исходный Markdown или генератор, а не руками собранный DOCX.
