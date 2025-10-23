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
        `tuple`: all program execution results

    '''
    return sum((
        (n,) if (
            (True if r is None else n == r) and \
            (_passed == len(i)) and \
            (_count == c if c else True) and \
            check(_steps + (_i,))
        ) else () if (
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
            _steps=_steps + (_i,)
        ) for _i, n in enumerate(commands(n))),
        start=()
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
        ], check=lambda steps: not (2, 2) in zip(steps, steps[1:]))),
        3162: lambda: len(f(2, 12, commands=lambda n: [
            n + 1,
            n + 2,
            n * 2,
        ], check=lambda steps: steps.count(2) == 1)),
        4275: lambda: len(f(2, 200, commands=lambda n: [
            n + 2,
            n * 3,
            n * 5,
        ], check=lambda steps: (steps.count(1) + steps.count(2)) <= 3)),
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


if __name__ == '__main__':
    test()
