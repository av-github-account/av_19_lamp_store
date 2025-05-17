VENV_DIR=.venv
REQ=requirements.dev.txt
ACTIVATE=. $(VENV_DIR)/bin/activate

.PHONY: help install venv run lint typecheck format clean a d

help:
	@echo "Доступные команды:"
	@echo "  make venv        — создать виртуальное окружение"
	@echo "  make install     — установить зависимости"
	@echo "  make run         — запустить FastAPI"
	@echo "  make lint        — проверить код ruff"
	@echo "  make format      — автоформатирование ruff"
	@echo "  make typecheck   — проверка типов mypy"
	@echo "  make clean       — удалить виртуальное окружение"
	@echo "  make a    		  — запуск виртуального окружения"
	@echo "  make d    		  — остановка виртуального окружения"

venv:
	uv venv $(VENV_DIR)

install:
	source $(VENV_DIR)/bin/activate && uv pip install -r $(REQ)

run:
	source $(VENV_DIR)/bin/activate && uvicorn app.main:app --reload --port 8001

lint:
	source $(VENV_DIR)/bin/activate && ruff check app

format:
	source $(VENV_DIR)/bin/activate && ruff format app

typecheck:
	source $(VENV_DIR)/bin/activate && mypy app

clean:
	rm -rf $(VENV_DIR)

a:
	@echo "source $(VENV_DIR)/bin/activate"


d:
	@echo "deactivate"