from app.config import Settings, validate_settings


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {"bot_token": "1:abc", "api_key": "key"}
    values.update(overrides)
    return Settings(_env_file=None, **values)  # type: ignore[arg-type]


def test_polling_needs_only_token_and_api_key() -> None:
    assert validate_settings(_settings()) == []


def test_missing_token_and_api_key_are_reported() -> None:
    errors = validate_settings(_settings(bot_token="", api_key=""))
    assert len(errors) == 2


def test_webhook_requires_https_base_url() -> None:
    config = _settings(
        bot_mode="webhook", webhook_secret="abcdefghijklmnop", webhook_base_url="http://x.test"
    )
    assert any("https" in error for error in validate_settings(config))


def test_webhook_requires_strong_secret() -> None:
    config = _settings(
        bot_mode="webhook", webhook_secret="short", webhook_base_url="https://bot.example.com"
    )
    assert any("WEBHOOK_SECRET" in error for error in validate_settings(config))


def test_valid_webhook_config_passes() -> None:
    config = _settings(
        bot_mode="webhook",
        webhook_secret="abcdefghijklmnop_-123",
        webhook_base_url="https://bot.example.com",
    )
    assert validate_settings(config) == []
