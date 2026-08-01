# QuantBet - Sistema de Arbitraje Deportivo Automatizado

[![CI](https://github.com/viensa90/QuantBet/actions/workflows/ci.yml/badge.svg)](https://github.com/viensa90/QuantBet/actions/workflows/ci.yml)
[![Tests de Estrés](https://github.com/viensa90/QuantBet/actions/workflows/stress.yml/badge.svg)](https://github.com/viensa90/QuantBet/actions/workflows/stress.yml)
[![codecov](https://codecov.io/gh/viensa90/QuantBet/branch/main/graph/badge.svg)](https://codecov.io/gh/viensa90/QuantBet)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 📊 Descripción

QuantBet es una plataforma de inteligencia cuantitativa para mercados de predicción deportiva. Implementa estrategias de:

- **Arbitraje** - Detección de diferencias de odds entre bookmakers
- **Value Betting** - Identificación de apuestas con valor usando modelos de probabilidad
- **Dutching** - Cobertura de múltiples resultados para beneficio garantizado

## 🚀 Características

- ✅ **Multi-mercado:** 1X2, Over/Under, Asian Handicap, Double Chance
- ✅ **Múltiples estrategias:** Arbitraje, Value Betting, Dutching
- ✅ **Modelos de probabilidad:** Historical, Elo, Poisson
- ✅ **Conectores:** CSV (ejemplo) y Web (Playwright)
- ✅ **Dashboard:** Visualización en tiempo real con Flask
- ✅ **Base de datos optimizada:** Índices, WAL, cache
- ✅ **Tests de estrés:** 5,000+ eventos validados
- ✅ **CI/CD:** GitHub Actions con tests automáticos

## 📦 Instalación

```bash
# Clonar repositorio
git clone https://github.com/viensa90/QuantBet.git
cd QuantBet

# Instalar dependencias
make install

# Verificar instalación
python main.py --help
🎯 Uso
CLI
# Ejecutar pipeline completo con datos CSV
python main.py --mode all --source csv

# Ejecutar solo arbitraje
python main.py --mode arbitrage

# Ejecutar value betting con modelo histórico
python main.py --mode value

# Iniciar dashboard web
python main.py --serve

# Ver estadísticas de la base de datos
python main.py --stats

# Limpiar datos antiguos (30 días)
python main.py --cleanup 30
Dashboard
Acceder a http://localhost:5000 para visualizar:

Resumen de mercados

Últimos snapshots

Top oportunidades

Estadísticas en tiempo real

🧪 Tests
# Ejecutar todos los tests (excepto estrés)
make test

# Ejecutar tests de estrés (5,000+ eventos)
make stress

# Ver cobertura
make coverage
📁 Estructura del Proyecto
QuantBet/
├── src/
│   ├── core/          # Motor de estrategias
│   ├── storage/       # Base de datos optimizada
│   ├── connectors/    # Fuentes de datos
│   ├── domain/        # Entidades
│   └── web/           # Dashboard Flask
├── tests/             # Tests unitarios y de estrés
├── data/              # Datos de ejemplo
├── .github/           # Workflows CI/CD
├── main.py            # CLI
├── config.yaml        # Configuración
└── requirements.txt   # Dependencias
🔧 Configuración
Editar config.yaml para personalizar:
strategies:
  arbitrage: true
  value_betting: true
  dutching: true

markets:
  enabled:
    - "1X2"
    - "Over/Under"

thresholds:
  min_profit_percent: 1.5
  min_value_probability: 0.65

probability_model:
  type: "historical"  # historical | elo | poisson
  📈 Rendimiento
50+ tests incluyendo estrés

5,000+ eventos procesados en < 10 segundos

Base de datos optimizada con índices y WAL

Cobertura de código > 70%

🤝 Contribución
Fork el repositorio

Crear una rama (git checkout -b feature/mejora)

Commitear cambios (git commit -am 'Añadir mejora')

Push a la rama (git push origin feature/mejora)

Crear Pull Request

📝 Licencia
MIT License - ver LICENSE para más detalles.

👨‍💻 Autor
viensa90 - GitHub

🏷️ Versiones
Versión	Fecha	Características
v0.3.1	31/07/2026	Optimización de BD + Tests de estrés
v0.3.0	31/07/2026	Multi-mercado + Modelos de probabilidad
v0.2.0	30/07/2026	Value Betting + Dutching
v0.1.0	29/07/2026	Lanzamiento inicial
🔗 Enlaces útiles:

Repositorio: https://github.com/viensa90/QuantBet

Dashboard: https://github.com/viensa90/QuantBet#dashboard

Documentación: https://github.com/viensa90/QuantBet/tree/main/QBMM