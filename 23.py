from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit.key_binding import KeyBindings
from pygments.lexers.python import PythonLexer
from pygments.styles import get_style_by_name
from pygments import lex
from typing import Callable


def f(n: int, r: int = None, i: tuple[int] = (), e: tuple[int] = (), c: int = None,
      *, commands: Callable[[int], list[int]], check: Callable[[tuple[int]], bool] = lambda _: True,
      _passed: int = 0, _count: int = 1, _steps: tuple = ()):
    '''
    Args:
        n (`int`): the original number
        r (`int`, optional): the result number
        i (`tuple[int]`, optional): values that must be included
        e (`tuple[int]`, optional): values that must be excluded
        c (`int`, optional): the number of program commands
        commands (`Callable`): the function that should return a list of commands
        check (`Callable`, optional): the function for creating conditions in the selection of commands

    Returns:
        `tuple` or `int`: all program execution results

    '''
    return sum((
        ((n,) if r is None else 1) if (
            (True if r is None else n == r) and \
            (_passed == len(i)) and \
            (_count == c if c else True) and \
            check(_steps + (_i + 1,))
        ) else (() if r is None else 0) if (
            (r is not None and (n < r if (n > commands(n)[0]) else n > r)) or \
            (n in e) or \
            (c and _count > c) or \
            (_passed > len(i))
        ) else f(
            n, r, i, e, c,
            commands=commands,
            check=check,
            _passed=_passed + (n in i),
            _count=_count + 1,
            _steps=_steps + (_i + 1,)
        ) for _i, n in enumerate(commands(n))),
        start=() if r is None else 0
    )


def test():
    tasks = {
        413: lambda: len(f(1, 15, commands=lambda n: [
            n + 1,
            n + 3,
            n * 2,
        ])),
        633: lambda: len(f(5, 154, commands=lambda n: [
            n + 1,
            n * 2,
            n ** 2,
        ])),
        2344: lambda: len(f(1, 13, commands=lambda n: [
            n + 1,
            n + 2,
            n * 4,
        ])),
        1301: lambda: len(f(23, 2, commands=lambda n: [
            n - 2,
            n - 5,
        ])),
        2345: lambda: len(f(22, 2, commands=lambda n: [
            n - 1,
            n - 3,
            n // 3,
        ])),
        20: lambda: len(f(1, 20, (10,), commands=lambda n: [
            n + 1,
            n * 2,
        ])),
        1037: lambda: len(f(1, 30, (12,), commands=lambda n: [
            n + 1,
            n * 2,
        ])),
        65: lambda: len(f(3, 20, (9, 12), commands=lambda n: [
            n + 1,
            n + 3,
            n * 2,
        ])),
        1376: lambda: len(f(102, 5, (43,), commands=lambda n: [
            n - 8,
            n // 2,
        ])),
        222: lambda: len(f(1, 63, (25,), (6,), commands=lambda n: [
            n + 2,
            n * 3,
        ])),
        951: lambda: len(f(4, 23, (8,), (11, 18), commands=lambda n: [
            n + 1,
            n + 2,
            n * 3,
        ])),
        104: lambda: len(f(1, 15, commands=lambda n: [
            n + 1,
            n * 2,
            n * 2 + 1,
            n * 10,
        ])),
        473: lambda: len(f(7, 63, (), (43,), commands=lambda n: [
            n + 2,
            n * 2 - 1,
            n * 2 + 1,
        ])),
        1137: lambda: len(f(0b100, 0b11101, commands=lambda n: [
            n + 1,
            n << 1,
            (n << 1) + 1,
        ])),
        2342: lambda: len(f(25, 51, commands=lambda n: [
            n + 1,
            int(''.join(str(int(i)+1) if i != '9' else '9' for i in str(n))),
        ])),
        2343: lambda: len(f(1, 20, commands=lambda n: [
            n + 1,
        ] + ([n * 1.5] if not n % 2 else []))),
        2340: lambda: next(r for r in range(31, 100000) if len(f(31, r, commands=lambda n: [
            n + 2,
            n + 4,
            n + 5,
        ])) == 1001),
        886: lambda: len(f(3, 27, c=7, commands=lambda n: [
            n + 1,
            n + 4,
            n * 2,
        ])),
        2339: lambda: len(set(f(1, c=15, commands=lambda n: [
            n * 2,
            n * 2 + 1,
        ]))),
        2341: lambda: sum(1 for r in set(f(1, c=8, commands=lambda n: [
            n + 1,
            n + 5,
            n * 3,
        ])) if 1000 <= r <= 1024),
        3030: lambda: len(f(1, 15, commands=lambda n: [
            n + 1,
            n + 2,
            n * 2,
        ], check=lambda steps: not (3, 3) in zip(steps, steps[1:]))),
        3162: lambda: len(f(2, 12, commands=lambda n: [
            n + 1,
            n + 2,
            n * 2,
        ], check=lambda steps: steps.count(3) == 1)),
        4275: lambda: len(f(2, 200, commands=lambda n: [
            n + 2,
            n * 3,
            n * 5,
        ], check=lambda steps: (steps.count(2) + steps.count(3)) <= 3)),
        4492: lambda: len(f(2, 40, type('', (), {
            '__len__': lambda _: 1,
            '__contains__': lambda _, v: v in range(3, 40, 2)
        })(), commands=lambda n: [
            n + 1,
            n + 2,
            n * 2,
        ])),
        2714: lambda: len(f(3, 25, type('', (), {
            '__len__': lambda _: 6,
            '__contains__': lambda _, v: v in range(4, 25, 2)
        })(), commands=lambda n: [
            n + 1,
            n + 3,
            n + 5,
        ])),
    }
    for number, answer in tasks.items():
        print(f'{number}. {answer()}')


def main():
    style = style_from_pygments_cls(get_style_by_name('lightbulb'))
    session_multiline = PromptSession(style=style, lexer=PygmentsLexer(PythonLexer))
    session = PromptSession(style=style, lexer=PygmentsLexer(PythonLexer))

    def prompt(message, *args, **kwargs):
        tokens = list(lex(message, PythonLexer()))
        return session.prompt(PygmentsTokens(tokens[:-1]), *args, **kwargs)

    binding = KeyBindings()
    @binding.add('enter')
    def _(event):
        buffer = event.current_buffer
        if not buffer.text or buffer.text.endswith('\n\n'):
            buffer.validate_and_handle()
        else:
            buffer.insert_text('\n')
    @binding.add('tab')
    def _(event):
        event.current_buffer.insert_text('    ')
    
    context = {}

    print('You can write code that be used as global variables:')
    exec(session_multiline.prompt(multiline=True, key_bindings=binding), context)

    print('Enter the function to define commands list (the int argument is given as n):')
    commands = eval('lambda n: ' + prompt('lambda n: '), context)

    print('Enter the original number:')
    number = int(eval(prompt('n = '), context))

    print('Enter the result number (empty for none):')
    result = int(eval(_, context)) if (_ := prompt('r = ', placeholder='None')) else None

    print('Enter the tuple for values that must be included:')
    included = eval(_, context) if (_ := prompt('i = ', placeholder='()')) else ()
    if isinstance(included, int):
        included = (included,)
    
    print('Enter the tuple for values that must be excluded:')
    excluded = eval(_, context) if (_ := prompt('e = ', placeholder='()')) else ()
    if isinstance(excluded, int):
        excluded = (excluded,)
    
    print('Enter the count of commands (empty for none):')
    count = int(eval(_, context)) if (_ := prompt('c = ', placeholder='None')) else None

    print('Enter the function for selecting commands (empty for none) (the tuple[int] argument is given as nums):')
    check = eval('lambda l: ' + (prompt('lambda l: ', placeholder='True') or 'True'), context)

    answer = f(number, result, included, excluded, count, commands=commands, check=check)
    
    print('\nTo get the answer you need, write the code or the result of the algorithm given as the answer variable:')
    print('\nResult:', eval(prompt('lambda answer: ', placeholder=''), context, {'answer': answer}))


if __name__ == '__main__':
    main()
