from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    database_url: str = "postgresql://signaltrade:signaltrade-local@localhost:5432/signaltrade"
    aws_region: str = "ap-northeast-2"
    sqs_endpoint_url: str = ""
    sqs_trading_command_queue_name: str = "signaltrade-trading-commands"
    sqs_strategy_command_queue_name: str = "signaltrade-strategy-commands"
    sqs_notification_queue_name: str = "signaltrade-notifications"
    outbox_poll_seconds: float = 1.0
    outbox_max_attempts: int = 10
    metrics_enabled: bool = True
    messaging_metrics_port: int = 9105
    log_level: str = "INFO"


settings = Settings()
