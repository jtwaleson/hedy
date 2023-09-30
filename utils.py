from flask import session, request, jsonify, make_response
from website.flask_helpers import render_template
from bs4 import BeautifulSoup
import contextlib
import datetime
import time
import functools
import os
import re
import string
import random
import uuid
import unicodedata
import traceback

from flask_babel import gettext, format_date, format_datetime, format_timedelta
from ruamel import yaml
import commonmark
from bs4.element import ResultSet
from io import BufferedWriter
from typing import Iterator

commonmark_parser = commonmark.Parser()
commonmark_renderer = commonmark.HtmlRenderer()

IS_WINDOWS = os.name == 'nt'

# Define code that will be used if some turtle command is present
with open('prefixes/turtle.py', encoding='utf-8') as f:
    TURTLE_PREFIX_CODE = f.read()

# Preamble that will be used for non-Turtle programs
# numerals list generated from: https://replit.com/@mevrHermans/multilangnumerals
with open('prefixes/normal.py', encoding='utf-8') as f:
    NORMAL_PREFIX_CODE = f.read()

# Define code that will be used if a pressed command is used
with open('prefixes/pygame.py', encoding='utf-8') as f:
    PYGAME_PREFIX_CODE = f.read()


class Timer:
    """A quick and dirty timer."""

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, tb):
        delta = time.time() - self.start
        print(f'{self.name}: {delta}s')


def timer(fn):
    """Decoractor for fn."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with Timer(fn.__name__):
            return fn(*args, **kwargs)
    return wrapper


def timems():
    """Return the UNIX timestamp in milliseconds.

    You only need to use this function if you are doing performance-sensitive
    timing. Otherwise, `times` (which returns second-resolution) is probably
    a better choice.
    """
    return int(round(time.time() * 1000))


def times():
    """Return the UNIX timestamp in seconds.

    If you need to store a date/time in the database, prefer this function.
    """
    return int(round(time.time()))


DEBUG_MODE = False


def is_debug_mode() -> bool:
    """Return whether or not we're in debug mode.

    We do more expensive things that are better for development in debug mode.
    """
    return DEBUG_MODE


def set_debug_mode(debug_mode: bool) -> None:
    """Switch debug mode to given value."""
    global DEBUG_MODE
    DEBUG_MODE = debug_mode


def load_yaml_rt(filename):
    """Load YAML with the round trip loader."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return yaml.round_trip_load(f, preserve_quotes=True)
    except IOError:
        return {}


def dump_yaml_rt(data):
    """Dump round-tripped YAML."""
    return yaml.round_trip_dump(data, indent=4, width=999)


def slash_join(*args) -> str:
    ret = []
    for arg in args:
        if not arg:
            continue

        if ret and not ret[-1].endswith('/'):
            ret.append('/')
        ret.append(arg.lstrip('/') if ret else arg)
    return ''.join(ret)


def is_testing_request(request):
    """Whether the current request is a test request.

    Test requests are performed by the e2e tests and have special privileges
    to do things other requests cannot do.

    Test requests are only allowed on non-Heroku instances.
    """
    return not is_heroku() and bool('X-Testing' in request.headers and request.headers['X-Testing'])


def extract_bcrypt_rounds(hash: str) -> int:
    return int(re.match(r'\$2b\$\d+', hash)[0].replace('$2b$', ''))


def isoformat(timestamp):
    """Turn a timestamp into an ISO formatted string."""
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    return dt.isoformat() + 'Z'


def is_production() -> bool:
    """Whether we are serving production traffic."""
    return os.getenv('IS_PRODUCTION', '') != ''


def is_heroku() -> bool:
    """Whether we are running on Heroku.

    Only use this flag if you are making a decision that really has to do with
    Heroku-based hosting or not.

    If you are trying to make a decision whether something needs to be done
    "for real" or not, prefer using:

    - `is_production()` to see if we're serving customer traffic and trying to
      optimize for safety and speed.
    - `is_debug_mode()` to see if we're on a developer machine and we're trying
      to optimize for developer productivity.

    """
    return os.getenv('DYNO', '') != ''


def version():
    # """Get the version from the Heroku environment variables."""
    if not is_heroku():
        return 'DEV'

    vrz = os.getenv('HEROKU_RELEASE_CREATED_AT')
    the_date = datetime.date.fromisoformat(vrz[:10]) if vrz else datetime.date.today()

    commit = os.getenv('HEROKU_SLUG_COMMIT', '????')[0:6]
    return the_date.strftime('%Y %b %d') + f'({commit})'


def valid_email(s):
    return bool(re.match(r'^(([a-zA-Z0-9_+\.\-]+)@([\da-zA-Z\.\-]+)\.([a-zA-Z\.]{2,6})\s*)$', s))


@contextlib.contextmanager
def atomic_write_file(filename: str, mode: str = 'wb') -> Iterator[BufferedWriter]:
    """Write to a filename atomically.

    First write to a unique tempfile, then rename the tempfile into
    place. Use replace instead of rename to make it atomic on windows as well.
    Use as a context manager:

        with atomic_write_file('file.txt') as f:
            f.write('hello')
    """

    tmp_file = f'{filename}.{os.getpid()}'
    with open(tmp_file, mode) as f:
        yield f

    os.replace(tmp_file, filename)


# This function takes a date in milliseconds from the Unix epoch and transforms it into a printable date
# It operates by converting the date to a string, removing its last 3 digits, converting it back to an int
# and then invoking the `isoformat` date function on it
def mstoisostring(date):
    return datetime.datetime.fromtimestamp(int(str(date)[:-3])).isoformat()


def string_date_to_date(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d")


def timestamp_to_date(timestamp, short_format=False):
    try:
        if short_format:
            return datetime.datetime.fromtimestamp(int(str(timestamp)))
        else:
            return datetime.datetime.fromtimestamp(int(str(timestamp)[:-3]))
    except BaseException:
        return None


def delta_timestamp(date, short_format=False):
    if short_format:
        delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(int(str(date)))
    else:
        delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(int(str(date)[:-3]))
    return format_timedelta(delta)


def stoisostring(date):
    return datetime.datetime.fromtimestamp(date)


def localized_date_format(date, short_format=False):
    # Improve the date by using the Flask Babel library and return timestamp as expected by language
    if short_format:
        timestamp = datetime.datetime.fromtimestamp(int(str(date)))
    else:
        timestamp = datetime.datetime.fromtimestamp(int(str(date)[:-3]))
    return format_date(timestamp, format='medium') + " " + format_datetime(timestamp, "H:mm")


def datetotimeordate(date):
    print(date)
    return date.replace("T", " ")


# https://stackoverflow.com/a/2257449


def random_id_generator(
        size=6,
        chars=string.ascii_uppercase +
        string.ascii_lowercase +
        string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# This function takes a Markdown string and returns a list with each of the HTML elements obtained
# by rendering the Markdown into HTML.


def markdown_to_html_tags(markdown: str) -> ResultSet:
    _html = commonmark_renderer.render(commonmark_parser.parse(markdown))
    soup = BeautifulSoup(_html, 'html.parser')
    return soup.find_all()


def error_page(error=404, page_error=None, ui_message=None, menu=True, iframe=None, exception=None):
    if error not in [403, 404, 500]:
        error = 404
    default = gettext('default_404')
    if error == 403:
        default = gettext('default_403')
    elif error == 500:
        default = gettext('default_500')

    hx_request = bool(request.headers.get('Hx-Request'))
    if hx_request:
        # For HTMX-request, just return the error as plain text body
        return make_response(f'{default} {exception}', error)

    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        # Produce a JSON response instead of an HTML response
        return jsonify({"code": error,
                        "error": default,
                        "exception": traceback.format_exception(type(exception), exception, exception.__traceback__) if exception else None}), error

    return render_template("error-page.html", menu=menu, error=error, iframe=iframe,
                           page_error=page_error or ui_message or '', default=default), error


def session_id():
    """Returns or sets the current session ID."""
    if 'session_id' not in session:
        if os.getenv('IS_TEST_ENV') and 'X-session_id' in request.headers:
            session['session_id'] = request.headers['X-session_id']
        else:
            session['session_id'] = uuid.uuid4().hex
    return session['session_id']


# https://github.com/python-babel/babel/issues/454
def customize_babel_locale(custom_locales: dict) -> None:
    from babel.core import get_global
    db = get_global('likely_subtags')
    for custom_name in custom_locales:
        db[custom_name] = custom_name
    import babel.localedata

    o_exists, o_load = babel.localedata.exists, babel.localedata.load
    if o_exists.__module__ != __name__:
        def exists(name):
            name = custom_locales.get(name, name)
            return o_exists(name)

        def load(name, merge_inherited=True):
            name = custom_locales.get(name, name)
            return o_load(name, merge_inherited)

        babel.localedata.exists = exists
        babel.localedata.load = load


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def base_url():
    """Return the base URL, excluding the leading slash

    Returns either from configuration or otherwise from Flask.
    """
    url = os.getenv('BASE_URL')
    if not url:
        url = request.host_url

    return url if not url.endswith('/') else url[:-1]
