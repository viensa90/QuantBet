# QuantBet Makefile
# Comandos útiles para desarrollo

.PHONY: help install test lint format coverage stress serve clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install    - Instalar dependencias"
	@echo "  make test       - Ejecutar tests (rápidos)"
	@echo "  make stress     - Ejecutar tests de estrés"
	@echo "  make lint       - Verificar linting"
	@echo "  make format     - Formatear código con Black"
	@echo "  make coverage   - Generar reporte de cobertura"
	@echo "  make serve      - Iniciar dashboard web"
	@echo "  make clean      - Limpiar archivos temporales"

install:
	pip install -r requirements.txt
	playwright install --with-deps chromium

test:
	pytest tests/ -v -m "not slow"

stress:
	pytest tests/test_stress.py -v --run-slow

lint:
	flake8 src/ tests/ --count --max-complexity=10 --statistics
	mypy src/ --ignore-missing-imports --no-strict-optional

format:
	black src/ tests/

coverage:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term -m "not slow"
	@echo "Reporte de cobertura generado en htmlcov/index.html"

serve:
	python main.py --serve

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf quantbet.db
	@echo "Limpieza completada"