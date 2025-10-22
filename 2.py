from prompt_toolkit import Application, PromptSession
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import DynamicContainer
from prompt_toolkit.layout import Layout, HSplit, Window, Container
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from typing import Callable, Generator
from itertools import product, permutations
import re


ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
NUMBERS = '0123456789'
OPERATORS = {
    '¬': ('!', 'not'),
    '∧': ('&', '*', 'and'),
    '∨': ('|', '+', 'or'),
    '≡': ('=', 'eq'),
    '→': ('>', 'impl'),
    '?': ('_')
}
TRANSLATE = {
    '¬': 'not ',
    '∧': ' and ',
    '∨': ' or ',
    '≡': '==',
    '→': '<=',
}
ALLOWED_FORMULA_SYMBOLS = ALPHABET + ''.join(OPERATORS.keys()) + '( ?)'


class FormulaEditor:
    def __init__(self) -> None:
        self.session = PromptSession()
        self.formula = ''
        buffer = self.session.default_buffer
        buffer.on_text_changed += self._on_text_changed
        buffer.on_cursor_position_changed += self._on_cursor_position_changed

    def _process_text(self, text: str) -> str:
        args, formula = text.split(' =', 1)
        if formula.startswith(' '):
            formula = formula[1:]

        if self.formula != formula:
            args = '(' + ','.join(char for char in ALPHABET if char in formula) + ')'

        self.formula = formula

        for new, old in OPERATORS.items():
            for var in old:
                formula = formula.replace(var, new)
        return args + ' = ' + ''.join(char for char in formula if char in ALLOWED_FORMULA_SYMBOLS)

    def _on_text_changed(self, buffer: Buffer) -> None:
        start_pos = buffer.text.index(' =')
        buffer.text = self._process_text(buffer.text)
        buffer.cursor_position += buffer.text.index(' =') - start_pos

    def _on_cursor_position_changed(self, buffer: Buffer) -> None:
        index = buffer.text.index(' =')
        if buffer.cursor_position == index + 2:
            buffer.cursor_position = index - 1
        if buffer.cursor_position == index:
            buffer.cursor_position = index + 3

    def _fetch_data(self, text: str) -> tuple[set[str], str]:
        args, formula = text.split(' = ')
        return set(args[1:-1].split(',')), formula

    def _make_expression(self, variables: set[str], formula: str) -> tuple[Callable[..., int | bool]]:
        '''
        0. original:       ((y → ¬x) ∧ y ≡ w) ∧ z  
        1. remove spaces:  ((y→¬x)∧y≡w)∧z  
        2. replace not-defined operator via iterator
        3. separate (≡):   (((y→¬x)∧y)≡w)∧z  
        4. separate (→):   (((y→(¬x))∧y)≡w)∧z  
        5. translate:      (((y<=(not x)) and y)==w) and z
        '''
        formula = formula.replace(' ', '')

        def get_raw_formulas() -> Generator[str]:
            if '?' in formula:
                for operator in '∧∨≡→':
                    yield formula.replace('?', operator)
            else:
                yield formula
        
        def replace_handler(match):
            full = match.group(0)
            char = '≡' if '≡' in full else '→'

            def process(inner: str):
                left, right = inner.split(char, 1)
                return f'({left.strip()}){char}({right.strip()})'

            if full.startswith('(') and full.endswith(')'):
                return '(' + process(full[1:-1]) + ')'
            return process(full)

        def get_processed_formulas() -> Generator[Callable[..., int | bool]]:
            for formula in get_raw_formulas():
                for char in '≡→':
                    formula = re.sub(
                        rf'\([^()]*{char}[^()]*\)|[^()\s]+{char}[^()\s]+',
                        replace_handler, formula
                    )

                for old, new in TRANSLATE.items():
                    formula = formula.replace(old, new)
                yield eval('lambda ' + ','.join(variables) + ':' + formula)
        
        return tuple(get_processed_formulas())

    def run(self) -> tuple[tuple[Callable[..., int | bool]], set[str]]:
        text = self.session.prompt('F', default='() = ')
        variables, formula = self._fetch_data(text)
        return self._make_expression(variables, formula), variables


class TableEditor:
    def __init__(self, variables: set[str]) -> None:
        self.variables = variables
        self.headers = ['?'] * len(variables) + ['F']
        self.table = [[' '] * (len(variables) + 1)]
        self.row = 0
        self.col = 0

        self.key_bindings = self._setup_key_bindings()
        self.layout = Layout(DynamicContainer(self._genering_table))

    def _genering_table(self) -> Container:
        headers = []
        for col, header in enumerate(self.headers):
            is_focused = -1 == self.row and col == self.col
            style = 'bg="white"' if is_focused else ''
            headers.append(f'  <style {style}>{header}</style>  ')
        table = [
            Window(
                content=FormattedTextControl(
                    text=HTML(f'<style bg="ansiblue"><b>|{'|'.join(headers)}|</b></style>')
                ),
                height=1
            )
        ]

        for row, rows in enumerate(self.table):
            cells = []
            for col, value in enumerate(rows):
                is_focused = row == self.row and col == self.col
                style = 'bg="ansiblue"' if is_focused else ''
                cells.append(f'  <style {style}>{value}</style>  ')
            table.append(
                Window(
                    content=FormattedTextControl(
                        text=HTML('|' + '|'.join(cells) + '|')
                    ),
                    height=1
                )
            )
        return HSplit(table)

    def _setup_key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add('up')
        def _(event):
            if self.row >= 0 and self.table[self.row] == [' '] * len(self.headers):
                del self.table[self.row]
            if self.row >= 0:
                if self.col != len(self.table) - 1:
                    self.row -= 1

        @kb.add('down')
        def _(event):
            if self.row >= 0 and self.table[self.row] == [' '] * len(self.headers):
                del self.table[self.row]
                self.row -= 1
            if self.row < len(self.table) - 1:
                self.row += 1
            else:
                self._add_new_row()
                self.row = len(self.table) - 1

        @kb.add('left')
        def _(event):
            if self.col > 0:
                self.col -= 1

        @kb.add('right')
        def _(event):
            if self.col < len(self.headers) - 1:
                if self.row != -1 or self.col < len(self.headers) - 2:
                    self.col += 1

        @kb.add('tab')
        def _(event):
            self._move_to_next_cell()

        @kb.add('backspace')
        def _(event):
            self._set_cell_value(' ')

        for char in '01 ' + ALPHABET:
            @kb.add(char)
            def _(event, char=char):
                self._set_cell_value(char)
                self._move_to_next_cell()

        @kb.add('enter')
        def _(event):
            for i, row in enumerate(self.table):
                if row == [' '] * len(self.headers):
                    del self.table[i]
            event.app.exit()

        return kb

    def _set_cell_value(self, value) -> None:
        if self.row == -1:
            if value in ALPHABET + ' ':
                self.headers[self.col] = '?' if value == ' ' else value
        else:
            self.table[self.row][self.col] = value

    def _move_to_next_cell(self) -> None:
        if self.col < len(self.headers) - 1:
            if self.row != -1 or self.col < len(self.headers) - 2:
                self.col += 1
        else:
            if self.row >= 0 and self.table[self.row] == [' '] * len(self.headers):
                del self.table[self.row]
                self.row -= 1
            if self.row == len(self.table) - 1:
                self._add_new_row()
                self.row += 1
            self.col = 0

    def _add_new_row(self) -> None:
        self.table.append([' '] * len(self.headers))

    def run(self) -> tuple[list[tuple[str]], list[str]]:
        app = Application(
            layout=self.layout,
            key_bindings=self.key_bindings,
            full_screen=False,
            mouse_support=False
        )
        
        app.run()
        return self.table, self.headers


def main():
    formula_editor = FormulaEditor()
    functions, variables = formula_editor.run()
    table_editor = TableEditor(variables)
    original_table, headers = table_editor.run()

    def iterating_table(table: list[tuple[int | None]]) -> Generator[tuple[list[tuple[int]], dict[str, int]]]:
        if count := sum(sum(1 for i in rows if i in ' ' + ALPHABET) for rows in table):

            for values in product((0, 1), repeat=count):
                letters = {}
                sheet = [()] * len(table)
                counter = 0

                for row in range(len(table)):
                    for col in range(len(table[row])):
                        cell = table[row][col]
                        if cell in '01':
                            sheet[row] += (int(cell),)
                        else:
                            if cell in ALPHABET:
                                letters[cell] = int(values[counter])
                            sheet[row] += (int(values[counter]),)
                            counter += 1

                if len(set(sheet)) == len(sheet):
                    yield sheet, letters
        else:
            yield list(tuple(int(i) for i in row) for row in table), {}
    
    def matching_headers(letters: tuple[str]) -> bool:
        for l, h in zip(letters, headers):
            if h != '?' and l != h:
                return False
        return True

    def permutation_columns(table: list[tuple[int]], function: Callable[..., int | bool]) -> Generator[str]:
        for letters in permutations(variables):
            if matching_headers(letters) and all(function(**dict(zip(letters, row[:-1]))) == row[-1] for row in table):
                yield ''.join(letters)

    rows = set()
    cells = []
    operators = set()
    for index, function in enumerate(functions):
        for table, values in iterating_table(original_table):
            for letters in permutation_columns(table, function):
                rows.add(letters)
                if values:
                    cells.append(values)
                if len(functions) > 1:
                    operators.add('∧∨≡→'[index])
    if operators:
        print('Result:', ''.join(operators))
    if cells:
        print('Result:', ' | '.join(''.join(str(i[1]) for i in sorted(v.items())) for v in cells))
    if rows:
        print('Result:', ' | '.join(rows))


if __name__ == '__main__':
    main()
