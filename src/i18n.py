import gettext

import config


def translate(message: str, language: str = "") -> str:
    if not language or language not in config.i18n_SUPPORTED_LANGUAGES:
        language = config.i18n_DEFAULT_LANGUAGE

    return gettext.translation(
        config.i18n_DOMAIN, localedir=config.i18n_LOCALES_PATH, languages=[language]
    ).gettext(message)
