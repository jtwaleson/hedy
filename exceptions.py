import inspect
from typing import Optional

"""
    Any exception added in this file must be also added to error-messages.txt
    So we can translate the error message. The exception must also be assigned
    an Exception Type in the exception_types dictionary in statistics.py
"""


class HedyException(Exception):
    def __init__(self, error_code: str, **arguments) -> None:
        """Create a new HedyException.

        You should not create a HedyException directly. Instead, use any of
        the subclasses of HedyException below.

        The keyword arguments passed into this constructor become available
        in exception translation strings. In those arguments, the keywords
        'location' and 'line_number' are special: they will be used to indicate
        the error location in the client.
        """
        super().__init__(error_code)

        self.error_code = error_code
        self.arguments = arguments

    @property
    def error_location(self):
        """Return the location where the error was found.

        Returns either an array of [row, col] or just [row].

        If 'location' is part of the keyword arguments, return that.
        Otherwise, if 'line_number' is part of the keyword arguments, return that instead
        wrapped in a list so we are sure the return type is always a list.

        """
        if 'location' in self.arguments:
            return self.arguments['location']
        if 'line_number' in self.arguments:
            return [self.arguments['line_number']]
        return None


class WarningException(HedyException):
    """Fixed That For You warning/exception.

    Not really a failure case: instead it represents a warning to
    the user that they made a mistake we recovered for them.

    'fixed_code' and 'fixed_result' will contain the repaired
    code, and the result of compiling that repaired code.
    """

    def __init__(self, error_code: str, fixed_code: str, fixed_result: str, **arguments) -> None:
        super().__init__(error_code, **arguments)
        self.fixed_code = fixed_code
        self.fixed_result = fixed_result


class InvalidSpaceException(WarningException):
    def __init__(self, level, line_number, fixed_code, fixed_result):
        super().__init__('Invalid Space',
                         level=level,
                         line_number=line_number,
                         fixed_code=fixed_code,
                         fixed_result=fixed_result)


class ParseException(HedyException):
    def __init__(self, level: str, location: str, found: str, fixed_code: Optional[str] = None) -> None:
        super().__init__('Parse',
                         level=level,
                         location=location,
                         found=found,
                         # 'character_found' for backwards compatibility
                         character_found=found)

        # TODO (FH, 8 dec 21) many exceptions now support fixed code maybe we
        # should move it to hedyexception?
        self.fixed_code = fixed_code


class UnquotedEqualityCheckException(HedyException):
    def __init__(self, line_number: str) -> None:
        super().__init__('Unquoted Equality Check',
                         line_number=line_number)
        self.location = [line_number]


class AccessBeforeAssignException(HedyException):
    def __init__(self, name: str, access_line_number: str, definition_line_number: str) -> None:
        super().__init__('Access Before Assign',
                         name=name,
                         access_line_number=access_line_number,
                         line_number=access_line_number,
                         definition_line_number=definition_line_number)


class UndefinedVarException(HedyException):
    def __init__(self, name: str, line_number: str) -> None:
        super().__init__('Var Undefined',
                         name=name,
                         line_number=line_number)


class CyclicVariableDefinitionException(HedyException):
    def __init__(self, variable: str, line_number: str) -> None:
        super().__init__('Cyclic Var Definition',
                         variable=variable,
                         line_number=line_number)


class InvalidArgumentTypeException(HedyException):
    def __init__(self, command: str, invalid_type: str, allowed_types: str, invalid_argument: str, line_number: str) -> None:
        super().__init__('Invalid Argument Type',
                         command=command,
                         invalid_type=invalid_type,
                         allowed_types=allowed_types,
                         invalid_argument=invalid_argument,
                         line_number=line_number)


class InvalidTypeCombinationException(HedyException):
    def __init__(self, command: str, arg1: str, arg2: str, type1: str, type2: str, line_number: str) -> None:
        super().__init__('Invalid Type Combination',
                         command=command,
                         invalid_argument=arg1,
                         invalid_argument_2=arg2,
                         invalid_type=type1,
                         invalid_type_2=type2,
                         line_number=line_number)


class InvalidArgumentException(HedyException):
    def __init__(self, command: str, allowed_types: str, invalid_argument: str, line_number: str) -> None:
        super().__init__('Invalid Argument',
                         command=command,
                         allowed_types=allowed_types,
                         invalid_argument=invalid_argument,
                         line_number=line_number)


class WrongLevelException(HedyException):
    def __init__(self, working_level: str, offending_keyword: str, tip: str, line_number: str) -> None:
        super().__init__('Wrong Level',
                         working_level=working_level,
                         offending_keyword=offending_keyword,
                         tip=tip,
                         line_number=line_number)


class InputTooBigException(HedyException):
    def __init__(self, lines_of_code: str, max_lines: str) -> None:
        super().__init__('Too Big',
                         lines_of_code=lines_of_code,
                         max_lines=max_lines)


class InvalidCommandException(WarningException):
    def __init__(
            self,
            level,
            invalid_command,
            guessed_command,
            line_number,
            fixed_code,
            fixed_result):
        super().__init__('Invalid',
                         invalid_command=invalid_command,
                         level=level,
                         guessed_command=guessed_command,
                         line_number=line_number,
                         fixed_code=fixed_code,
                         fixed_result=fixed_result)
        self.location = [line_number]


class MissingCommandException(HedyException):
    def __init__(self, level: str, line_number: str) -> None:
        super().__init__('Missing Command',
                         level=level,
                         line_number=line_number)


class MissingInnerCommandException(HedyException):
    def __init__(self, command: str, level: str, line_number: str) -> None:
        super().__init__('Missing Inner Command',
                         command=command,
                         level=level,
                         line_number=line_number)


class InvalidAtCommandException(HedyException):
    def __init__(self, command: str, level: str, line_number: str) -> None:
        super().__init__('Invalid At Command',
                         command=command,
                         level=level,
                         line_number=line_number)


class IncompleteRepeatException(HedyException):
    def __init__(self, command: str, level: str, line_number: str) -> None:
        super().__init__('Incomplete Repeat',
                         command=command,
                         level=level,
                         line_number=line_number)


class LonelyTextException(HedyException):
    def __init__(self, level: str, line_number: str) -> None:
        super().__init__('Lonely Text',
                         level=level,
                         line_number=line_number)


class IncompleteCommandException(HedyException):
    def __init__(self, incomplete_command: str, level: str, line_number: str) -> None:
        super().__init__('Incomplete',
                         incomplete_command=incomplete_command,
                         level=level,
                         line_number=line_number)

        # Location is copied here so that 'hedy_error_to_response' will find it
        # Location can be either [row, col] or just [row]
        self.location = [line_number]


class UnquotedTextException(HedyException):
    def __init__(self, level: str, line_number: str, unquotedtext: Optional[str] = None) -> None:
        super().__init__('Unquoted Text',
                         level=level,
                         unquotedtext=unquotedtext,
                         line_number=line_number)


class UnquotedAssignTextException(HedyException):
    def __init__(self, text: str, line_number: str) -> None:
        super().__init__('Unquoted Assignment', text=text, line_number=line_number)


class LonelyEchoException(HedyException):
    def __init__(self) -> None:
        super().__init__('Lonely Echo')


class CodePlaceholdersPresentException(HedyException):
    def __init__(self, line_number: str) -> None:
        super().__init__('Has Blanks', line_number=line_number)


class NoIndentationException(HedyException):
    def __init__(self, line_number: str, leading_spaces: str, indent_size: str, fixed_code: Optional[str] = None) -> None:
        super().__init__('No Indentation',
                         line_number=line_number,
                         leading_spaces=leading_spaces,
                         indent_size=indent_size)
        self.fixed_code = fixed_code


class IndentationException(HedyException):
    def __init__(self, line_number: str, leading_spaces: str, indent_size: str, fixed_code: Optional[str] = None) -> None:
        super().__init__('Unexpected Indentation',
                         line_number=line_number,
                         leading_spaces=leading_spaces,
                         indent_size=indent_size)
        self.fixed_code = fixed_code


class UnsupportedFloatException(HedyException):
    def __init__(self, value: str) -> None:
        super().__init__('Unsupported Float', value=value)


class LockedLanguageFeatureException(HedyException):
    def __init__(self, concept: str) -> None:
        super().__init__('Locked Language Feature', concept=concept)


class UnsupportedStringValue(HedyException):
    def __init__(self, invalid_value: str) -> None:
        super().__init__('Unsupported String Value', invalid_value=invalid_value)


class MissingElseForPressitException(HedyException):
    def __init__(self, command: str, level: str, line_number: str) -> None:
        super().__init__('Pressit Missing Else',
                         command=command,
                         level=level,
                         line_number=line_number)


class NestedFunctionException(HedyException):
    def __init__(self) -> None:
        super().__init__('Nested Function')


HEDY_EXCEPTIONS = {name: cls for name, cls in globals().items() if inspect.isclass(cls)}
