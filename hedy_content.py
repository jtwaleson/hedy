import logging
import os

import static_babel_content

from utils import customize_babel_locale
from website.yaml_file import YamlFile
from safe_format import safe_format

logger = logging.getLogger(__name__)

COUNTRIES = static_babel_content.COUNTRIES

# Define dictionary for available languages. Fill dynamically later.
ALL_LANGUAGES = {}
ALL_KEYWORD_LANGUAGES = {}

# Todo TB -> We create this list manually, but it would be nice if we find
# a way to automate this as well
NON_LATIN_LANGUAGES = ['ar', 'bg', 'bn', 'el', 'fa', 'hi', 'he', 'pa_PK', 'ru', 'zh_Hans']

# Babel has a different naming convention than Weblate and doesn't support some languages -> fix this manually
CUSTOM_BABEL_LANGUAGES = {'pa_PK': 'pa_Arab_PK', 'kmr': 'ku_TR', 'tn': 'en', 'tl': 'en'}
# For the non-existing language manually overwrite the display language to make sure it is displayed correctly
CUSTOM_LANGUAGE_TRANSLATIONS = {'kmr': 'Kurdî (Tirkiye)', 'tn': 'Setswana', 'tl': 'ᜆᜄᜎᜓᜄ᜔'}
customize_babel_locale(CUSTOM_BABEL_LANGUAGES)

KEYWORDS_ADVENTURES = set([
    'print_command',
    'ask_command',
    'is_command',
    'sleep_command',
    'random_command',
    'add_remove_command',
    'quotation_marks',
    'if_command',
    'in_command',
    'maths',
    'repeat_command',
    'repeat_command_2',
    'for_command',
    'and_or_command',
    'while_command',
    'elif_command',
    'clear_command'
])

ADVENTURE_ORDER_PER_LEVEL = {
    1: [
        'default',
        'print_command',
        'ask_command',
        'parrot',
        'rock',
        'haunted',
        'story',
        'turtle',
        'restaurant',
        'fortune',
    ],
    2: [
        'default',
        'is_command',
        'rock',
        'ask_command',
        'rock_2',
        'haunted',
        'sleep_command',
        'parrot',
        'story',
        'restaurant',
        'turtle'
    ],
    3: [
        'default',
        'random_command',
        'dice',
        'rock',
        'fortune',
        'restaurant',
        'add_remove_command',
        'parrot',
        'dishes',
        'story',
        'haunted',
        'turtle'
    ],
    4: [
        'default',
        'quotation_marks',
        'rock',
        'dice',
        'dishes',
        'parrot',
        'turtle',
        'clear_command',
        'story',
        'haunted',
        'fortune',
        'restaurant'
    ],
    5: [
        'default',
        'if_command',
        'language',
        'dice',
        'dishes',
        'story',
        'rock',
        'parrot',
        'haunted',
        'in_command',
        'restaurant',
        'fortune',
        'pressit',
        'turtle'
    ],
    6: [
        'default',
        'maths',
        'songs',
        'dice',
        'dishes',
        'turtle',
        'calculator',
        'fortune',
        'restaurant'
    ],
    7: [
        'default',
        'repeat_command',
        'story',
        'songs',
        'dishes',
        'dice',
        'repeat_command_2',
        'fortune',
        'restaurant',
        'pressit'
    ],
    8: [
        'default',
        'repeat_command',
        'fortune',
        'repeat_command_2',
        'songs',
        'if_command',
        'story',
        'haunted',
        'restaurant',
        'turtle'
    ],
    9: [
        'default',
        'repeat_command',
        'rock',
        'story',
        'calculator',
        'restaurant',
        'haunted',
        'pressit',
        'turtle'
    ],
    10: [
        'default',
        'for_command',
        'dishes',
        'dice',
        'fortune',
        'harry_potter',
        'songs',
        'story',
        'rock',
        'calculator',
        'restaurant',
    ],
    11: [
        'default',
        'for_command',
        'years',
        'calculator',
        'songs',
        'restaurant',
        'haunted'
    ],
    12: [
        'default',
        'maths',
        'quotation_marks',
        'story',
        'fortune',
        'songs',
        'restaurant',
        'calculator',
        'piggybank',
        'secret'
    ],
    13: [
        'default',
        'and_or_command',
        'secret',
        'story',
        'rock',
        'restaurant',
        'calculator',
        'tic'
    ],
    14: [
        'default',
        'is_command',
        'haunted',
        'calculator',
        'piggybank',
        'quizmaster',
        'tic'
    ],
    15: [
        'default',
        'while_command',
        'restaurant',
        'story',
        'dice',
        'rock',
        'calculator',
        'tic'
    ],
    16: [
        'default',
        'random_command',
        'haunted',
        'songs',
        'language'
    ],
    17: [
        'default',
        'for_command',
        'elif_command',
        'tic',
        'blackjack'
    ],
    18: [
        'default',
        'print_command',
        'story',
        'songs'
    ]
}

RESEARCH = {}
for paper in sorted(os.listdir('content/research'),
                    key=lambda x: int(x.split("_")[-1][:-4]),
                    reverse=True):
    # An_approach_to_describing_the_semantics_of_Hedy_2022.pdf -> 2022, An
    # approach to describing the semantics of Hedy
    name = paper.replace("_", " ").split(".")[0]
    name = name[-4:] + ". " + name[:-5]
    RESEARCH[name] = paper

# load all available languages in dict
# list_translations of babel does about the same, but without territories.
languages = {}
if not os.path.isdir('translations'):
    # should not be possible, but if it's moved someday, EN would still be working.
    ALL_LANGUAGES['en'] = 'English'
    ALL_KEYWORD_LANGUAGES['en'] = 'EN'

for folder in os.listdir('translations'):
    locale_dir = os.path.join('translations', folder, 'LC_MESSAGES')
    if not os.path.isdir(locale_dir):
        continue
    if filter(lambda x: x.endswith('.mo'), os.listdir(locale_dir)):
        languages[folder] = CUSTOM_LANGUAGE_TRANSLATIONS.get(folder,
                                                             static_babel_content.LANGUAGE_NAMES.get(folder, folder))


for lang in sorted(languages):
    ALL_LANGUAGES[lang] = languages[lang]
    if os.path.exists('./grammars/keywords-' + lang + '.lark'):
        ALL_KEYWORD_LANGUAGES[lang] = lang[0:2].upper()  # first two characters

# Load and cache all keyword yamls
KEYWORDS = {}
for lang in ALL_KEYWORD_LANGUAGES.keys():
    KEYWORDS[lang] = YamlFile.for_file(f'content/keywords/{lang}.yaml').to_dict()
    for k, v in KEYWORDS[lang].items():
        if isinstance(v, str) and "|" in v:
            # when we have several options, pick the first one as default
            # Some keys are ints, turn them into strings
            KEYWORDS[lang][k] = v.split('|')[0]


class StructuredDataFile:
    """Base class for all data files in the content directory."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self._file = None

    @property
    def file(self):
        """Lazily load the requested file."""
        if not self._file:
            self._file = YamlFile.for_file(self.filename)
        return self._file


class Commands(StructuredDataFile):
    def __init__(self, language: str) -> None:
        self.language = language
        super().__init__(f'content/cheatsheets/{self.language}.yaml')

    def get_commands_for_level(self, level, keyword_lang):
        return deep_translate_keywords(self.file.get(int(level), {}), keyword_lang)


def deep_translate_keywords(yaml, keyword_language):
    try:
        """Recurse through a data structure and replace keyword placeholders in any strings we encounter."""
        if isinstance(yaml, str):
            # this is used to localize adventures linked in slides (PR 3860)
            yaml = yaml.replace('/raw', f'/raw?keyword_language={keyword_language}')
            return safe_format(yaml, **KEYWORDS.get(keyword_language))
        if isinstance(yaml, list):
            return [deep_translate_keywords(e, keyword_language) for e in yaml]
        if isinstance(yaml, dict):
            return {k: deep_translate_keywords(v, keyword_language) for k, v in yaml.items()}
        return yaml
    except ValueError as E:
        raise ValueError(f'Issue in language {keyword_language}. Offending yaml: {yaml}. Error: {E}')
    except TypeError as E:
        raise TypeError(f'Issue in language {keyword_language}. Offending yaml: {yaml}. Error: {E}')


def get_localized_name(name, keyword_lang):
    return safe_format(name, **KEYWORDS.get(keyword_lang))

# Todo TB -> We don't need these anymore as we guarantee with Weblate that
# each language file is there


class NoSuchCommand:
    def get_commands_for_level(self, level, keyword_lang):
        return {}


class Adventures(StructuredDataFile):
    def __init__(self, language: str) -> None:
        self.language = language
        super().__init__(f'content/adventures/{self.language}.yaml')

    def get_adventure_keyname_name_levels(self):
        return {aid: {adv['name']: list(adv['levels'].keys())} for aid, adv in self.file.get('adventures', {}).items()}

    def get_adventure_names(self):
        return {aid: adv['name'] for aid, adv in self.file.get('adventures', {}).items()}

    def get_adventures(self, keyword_lang="en"):
        return deep_translate_keywords(self.file.get('adventures'), keyword_lang)

    def has_adventures(self):
        return True if self.file.get('adventures') else False


class NoSuchAdventure:
    def get_adventure(self):
        return {}


class ParsonsProblem(StructuredDataFile):
    def __init__(self, language: str) -> None:
        self.language = language
        super().__init__(f'content/parsons/{self.language}.yaml')

    def get_highest_exercise_level(self, level):
        return max(int(lnum) for lnum in self.file.get('levels', {}).get(level, {}).keys())

    def get_parsons_data_for_level(self, level, keyword_lang="en"):
        return deep_translate_keywords(self.file.get('levels', {}).get(level, None), keyword_lang)

    def get_parsons_data_for_level_exercise(self, level, excercise, keyword_lang="en"):
        return deep_translate_keywords(self.file.get('levels', {}).get(level, {}).get(excercise), keyword_lang)


class Quizzes(StructuredDataFile):
    def __init__(self, language: str) -> None:
        self.language = language
        super().__init__(f'content/quizzes/{self.language}.yaml')

    def get_highest_question_level(self, level):
        return max(int(k) for k in self.file.get('levels', {}).get(level, {}))

    def get_quiz_data_for_level(self, level, keyword_lang="en"):
        return deep_translate_keywords(self.file.get('levels', {}).get(level), keyword_lang)

    def get_quiz_data_for_level_question(self, level, question, keyword_lang="en"):
        return deep_translate_keywords(self.file.get('levels', {}).get(level, {}).get(question), keyword_lang)


class NoSuchQuiz:
    def get_quiz_data_for_level(self, level, keyword_lang):
        return {}


class Tutorials(StructuredDataFile):
    # Want to parse the keywords only once, they can be cached -> perform this
    # action on server start
    def __init__(self, language: str) -> None:
        self.language = language
        super().__init__(f'content/tutorials/{self.language}.yaml')

    def get_tutorial_for_level(self, level, keyword_lang="en"):
        if level not in ["intro", "teacher"]:
            level = int(level)
        return deep_translate_keywords(self.file.get(level, None), keyword_lang)

    def get_tutorial_for_level_step(self, level, step, keyword_lang="en"):
        if level not in ["intro", "teacher"]:
            level = int(level)
        return deep_translate_keywords(self.file.get(level, {}).get('steps', {}).get(step), keyword_lang)


class NoSuchTutorial:
    def get_tutorial_for_level(self, level, keyword_lang):
        return {}


class Slides(StructuredDataFile):
    def __init__(self, language: str) -> None:
        self.language = language
        super().__init__(f'content/slides/{self.language}.yaml')

    def get_slides_for_level(self, level, keyword_lang="en"):
        return deep_translate_keywords(self.file.get('levels', {}).get(level), keyword_lang)


class NoSuchSlides:
    def get_slides_for_level(self, level, keyword_lang):
        return {}
