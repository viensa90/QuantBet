import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

class ConfigLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        # Cargar .env si existe
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            load_dotenv()

        # Cargar configuración YAML con codificación UTF-8 explícita
        config_path = Path(__file__).parent.parent / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

        # Sobrescribir claves sensibles con variables de entorno
        self._override_from_env()

    def _override_from_env(self):
        # Odds API
        if os.getenv('ODDS_API_KEY'):
            self._config.setdefault('odds_api', {})['key'] = os.getenv('ODDS_API_KEY')
        # Telegram
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self._config.setdefault('notifications', {}).setdefault('telegram', {})['bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN')
        if os.getenv('TELEGRAM_CHAT_ID'):
            self._config['notifications']['telegram']['chat_id'] = os.getenv('TELEGRAM_CHAT_ID')
        # Email
        for key in ['EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_USER', 'EMAIL_PASS']:
            env_val = os.getenv(key)
            if env_val:
                self._config.setdefault('notifications', {}).setdefault('email', {})[key.lower()] = env_val

    def get(self, key, default=None):
        return self._config.get(key, default)

    def __getitem__(self, key):
        return self._config[key]

    @property
    def odds_api_key(self):
        return self['odds_api']['key']

    @property
    def telegram_token(self):
        return self['notifications']['telegram']['bot_token']

    @property
    def telegram_chat_id(self):
        return self['notifications']['telegram']['chat_id']