"""
Configuración Swagger/OpenAPI para QuantBet Dashboard
Versión: 0.3.2
"""

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "QuantBet API",
        "description": (
            "Plataforma de inteligencia cuantitativa para mercados de predicción deportiva.\n\n"
            "### Estrategias implementadas:\n"
            "- **Arbitraje**: Detección de diferencias de odds entre bookmakers\n"
            "- **Value Betting**: Identificación de apuestas con valor\n"
            "- **Dutching**: Cobertura de múltiples resultados\n\n"
            "### Deportes soportados:\n"
            "- Fútbol (1X2, Over/Under, Asian Handicap, Double Chance)\n"
            "- Tenis (Winner, Set Handicap, Total Games)\n"
            "- Baloncesto (Moneyline, Spread, Total Points, Quarter Winner)"
        ),
        "version": "0.3.2",
        "contact": {
            "name": "QuantBet Team",
            "url": "https://github.com/viensa90/QuantBet"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "host": "localhost:5000",
    "basePath": "/api/v1",
    "schemes": ["http"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "tags": [
        {"name": "Dashboard", "description": "Métricas y resumen del sistema"},
        {"name": "Markets", "description": "Análisis de mercados deportivos"},
        {"name": "Opportunities", "description": "Oportunidades de apuesta detectadas"},
        {"name": "Snapshots", "description": "Histórico de snapshots procesados"},
        {"name": "System", "description": "Estado y configuración del sistema"}
    ],
    "paths": {
        "/metrics": {
            "get": {
                "tags": ["Dashboard"],
                "summary": "Obtener métricas del dashboard",
                "description": "Devuelve un resumen de todas las métricas del sistema: total de oportunidades, mercados activos, rendimiento de estrategias.",
                "responses": {
                    "200": {
                        "description": "Métricas obtenidas correctamente",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "total_opportunities": {"type": "integer", "example": 142},
                                "active_markets": {"type": "integer", "example": 8},
                                "strategies": {
                                    "type": "object",
                                    "properties": {
                                        "arbitrage": {"type": "integer", "example": 23},
                                        "value_betting": {"type": "integer", "example": 45},
                                        "dutching": {"type": "integer", "example": 12}
                                    }
                                },
                                "last_update": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                }
            }
        },
        "/markets": {
            "get": {
                "tags": ["Markets"],
                "summary": "Listar mercados activos",
                "description": "Devuelve la lista de mercados deportivos configurados y su estado.",
                "responses": {
                    "200": {
                        "description": "Lista de mercados",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "sport": {"type": "string", "example": "Fútbol"},
                                    "market_type": {"type": "string", "example": "1X2"},
                                    "event_count": {"type": "integer", "example": 12},
                                    "enabled": {"type": "boolean", "example": True}
                                }
                            }
                        }
                    }
                }
            }
        },
        "/opportunities": {
            "get": {
                "tags": ["Opportunities"],
                "summary": "Obtener oportunidades de apuesta",
                "description": "Devuelve las mejores oportunidades detectadas por el sistema.",
                "parameters": [
                    {
                        "name": "strategy",
                        "in": "query",
                        "type": "string",
                        "enum": ["arbitrage", "value_betting", "dutching"],
                        "description": "Filtrar por tipo de estrategia"
                    },
                    {
                        "name": "min_profit",
                        "in": "query",
                        "type": "number",
                        "format": "float",
                        "description": "Filtro de beneficio mínimo (%)"
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "type": "integer",
                        "description": "Número máximo de resultados a devolver",
                        "default": 10
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Oportunidades encontradas",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "event": {"type": "string", "example": "Real Madrid vs Barcelona"},
                                    "sport": {"type": "string", "example": "Fútbol"},
                                    "market_type": {"type": "string", "example": "1X2"},
                                    "strategy": {"type": "string", "example": "arbitrage"},
                                    "profit_percent": {"type": "number", "format": "float", "example": 2.5},
                                    "odds": {
                                        "type": "object",
                                        "example": {"1": 2.10, "X": 3.40, "2": 3.80}
                                    },
                                    "timestamp": {"type": "string", "format": "date-time"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "/snapshots": {
            "get": {
                "tags": ["Snapshots"],
                "summary": "Listar snapshots procesados",
                "description": "Devuelve el historial de snapshots procesados por el motor.",
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "type": "integer",
                        "description": "Número máximo de snapshots a devolver",
                        "default": 20
                    },
                    {
                        "name": "from_date",
                        "in": "query",
                        "type": "string",
                        "format": "date",
                        "description": "Fecha de inicio (YYYY-MM-DD)"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Lista de snapshots",
                        "schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "snapshot_id": {"type": "integer", "example": 42},
                                    "source": {"type": "string", "example": "CSV"},
                                    "event_count": {"type": "integer", "example": 15},
                                    "opportunity_count": {"type": "integer", "example": 3},
                                    "timestamp": {"type": "string", "format": "date-time"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "/system/status": {
            "get": {
                "tags": ["System"],
                "summary": "Estado del sistema",
                "description": "Devuelve información de estado del sistema, configuraciones y versiones.",
                "responses": {
                    "200": {
                        "description": "Estado del sistema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "version": {"type": "string", "example": "0.3.2"},
                                "status": {"type": "string", "enum": ["running", "degraded", "stopped"]},
                                "db_size_mb": {"type": "number", "format": "float", "example": 4.2},
                                "models_loaded": {"type": "array", "items": {"type": "string"}},
                                "connectors": {
                                    "type": "object",
                                    "properties": {
                                        "csv": {"type": "string", "enum": ["active", "inactive"]},
                                        "web": {"type": "string", "enum": ["active", "inactive"]}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/system/config": {
            "get": {
                "tags": ["System"],
                "summary": "Obtener configuración actual",
                "description": "Devuelve la configuración completa del sistema (valores sensibles ocultos).",
                "responses": {
                    "200": {
                        "description": "Configuración del sistema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "strategies": {
                                    "type": "object",
                                    "properties": {
                                        "arbitrage": {"type": "boolean"},
                                        "value_betting": {"type": "boolean"},
                                        "dutching": {"type": "boolean"}
                                    }
                                },
                                "markets": {"type": "array", "items": {"type": "string"}},
                                "thresholds": {
                                    "type": "object",
                                    "properties": {
                                        "min_profit_percent": {"type": "number"},
                                        "min_value_probability": {"type": "number"}
                                    }
                                },
                                "probability_model": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    },
    "definitions": {
        "Opportunity": {
            "type": "object",
            "required": ["event", "sport", "strategy", "profit_percent"],
            "properties": {
                "event_id": {"type": "string", "description": "ID único del evento"},
                "event": {"type": "string", "description": "Nombre del evento"},
                "sport": {"type": "string", "description": "Deporte"},
                "market_type": {"type": "string", "description": "Tipo de mercado"},
                "strategy": {"type": "string", "description": "Estrategia aplicada"},
                "profit_percent": {"type": "number", "description": "Beneficio esperado %"},
                "odds": {"type": "object", "description": "Odds involucradas"},
                "timestamp": {"type": "string", "format": "date-time"}
            }
        }
    }
}