.PHONY: help install install-backend install-frontend backend frontend dev

VENV_PYTHON := /home/nik/Desktop/REint.ai/venv/bin/python
VENV_PIP := /home/nik/Desktop/REint.ai/venv/bin/pip
BACKEND_DIR := /home/nik/Desktop/REint.ai/backend
FRONTEND_DIR := /home/nik/Desktop/REint.ai/frontend

help:
	@echo "Available targets:"
	@echo "  make install   Install backend and frontend dependencies"
	@echo "  make install-backend  Install backend Python dependencies"
	@echo "  make install-frontend Install frontend npm dependencies"
	@echo "  make backend   Start FastAPI backend only"
	@echo "  make frontend  Start frontend only"
	@echo "  make dev       Start backend and frontend together"

install: install-backend install-frontend

install-backend:
	@test -f $(BACKEND_DIR)/requirements.txt || (echo "backend/requirements.txt not found." && exit 1)
	@$(VENV_PIP) install -r $(BACKEND_DIR)/requirements.txt

install-frontend:
	@test -f $(FRONTEND_DIR)/package.json || (echo "frontend/package.json not found." && exit 1)
	@cd $(FRONTEND_DIR) && npm install

backend:
	@cd $(BACKEND_DIR) && $(VENV_PYTHON) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	@test -f $(FRONTEND_DIR)/package.json || (echo "frontend/package.json not found. Initialize the frontend app first." && exit 1)
	@cd $(FRONTEND_DIR) && npm run dev -- --host 127.0.0.1 --port 5173

dev:
	@test -f $(FRONTEND_DIR)/package.json || (echo "frontend/package.json not found. Initialize the frontend app first." && exit 1)
	@trap 'kill 0' INT TERM EXIT; \
	cd $(BACKEND_DIR) && $(VENV_PYTHON) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 & \
	cd $(FRONTEND_DIR) && npm run dev -- --host 127.0.0.1 --port 5173 & \
	wait
