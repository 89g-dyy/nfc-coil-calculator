"""The window ships English and Chinese strings; both catalogs must stay complete."""
import pytest

from nfc_coil_calculator.i18n import (MESSAGES, LANGUAGES, Message, ValidationError, default_language,
                                      text, translate)


def test_both_catalogs_define_the_same_keys():
    english = set(MESSAGES["en"])
    for language in LANGUAGES:
        assert set(MESSAGES[language]) == english, language


def test_missing_key_falls_back_to_english_then_to_the_key_itself():
    assert translate("zh", "no.such.key") == "no.such.key"
    assert translate("unknown", "app.title") == MESSAGES["en"]["app.title"]


def test_messages_keep_their_identifier_for_later_translation():
    message = Message("error.turns")
    assert str(message) == "Turns must be an integer between 1 and 15."
    assert text(message, "zh") == "匝数必须是 1～15 的整数。"
    assert text("plain", "zh") == "plain"


def test_validation_error_is_a_value_error_with_a_translatable_message():
    error = ValidationError("error.minimum_dimension", minimum=12.5)
    assert isinstance(error, ValueError)
    assert "12.5" in str(error)
    assert "12.5" in text(error.message, "zh")


def test_formatting_uses_locale_placeholders():
    assert translate("en", "status.saved", name="coil.json") == "Saved: coil.json"
    assert translate("zh", "status.saved", name="coil.json") == "已保存：coil.json"


def test_default_language_is_supported():
    assert default_language() in LANGUAGES


@pytest.mark.parametrize("language", LANGUAGES)
def test_parameter_keys_exist_in_every_language(language):
    from nfc_coil_calculator.params import PARAMETERS

    for _, label_key, _ in PARAMETERS:
        assert label_key in MESSAGES[language]
