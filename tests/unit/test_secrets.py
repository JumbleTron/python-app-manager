from python_app_manager.utils.secrets import generate_password, generate_secret_key


def test_secret_key_has_requested_entropy_and_is_unique() -> None:
    first = generate_secret_key()
    second = generate_secret_key()

    assert len(first) >= 64
    assert first != second


def test_password_has_requested_entropy() -> None:
    assert len(generate_password()) >= 43
