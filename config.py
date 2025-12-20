"""
Конфигурация проекта.

Содержит настройки бота, базы данных и другие параметры.
Секреты загружаются из переменных окружения через .env файл.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # Токен бота
    bot_token: str = Field(..., env="BOT_TOKEN", description="Токен Telegram бота")
    
    # Настройки базы данных
    db_host: str = Field(default="localhost", env="DB_HOST", description="Хост БД")
    db_port: int = Field(default=5432, env="DB_PORT", description="Порт БД")
    db_name: str = Field(..., env="DB_NAME", description="Имя базы данных")
    db_user: str = Field(..., env="DB_USER", description="Пользователь БД")
    db_password: str = Field(..., env="DB_PASSWORD", description="Пароль БД")
    
    # ID администраторов (строка через запятую, например: "123456789,987654321")
    admin_ids_str: str = Field(default="", env="ADMIN_IDS", description="Список ID администраторов через запятую")
    
    @property
    def admin_ids(self) -> list[int]:
        """Получить список ID администраторов.
        
        Returns:
            Список ID администраторов
        """
        if not self.admin_ids_str:
            return []
        return [int(id.strip()) for id in self.admin_ids_str.split(",") if id.strip()]
    
    # Настройки логирования
    log_level: str = Field(default="INFO", env="LOG_LEVEL", description="Уровень логирования")
    log_file: str = Field(default="bot.log", env="LOG_FILE", description="Файл для логов")
    
    class Config:
        """Конфигурация Pydantic."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()
