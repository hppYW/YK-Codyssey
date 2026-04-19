import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout,
    QPushButton, QVBoxLayout, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt


class Calculator(QWidget):
    '''아이폰 스타일 계산기 UI 및 4칙연산 기능'''

    def __init__(self):
        super().__init__()
        self._expression = ''      # 내부 계산용 수식
        self._display_text = '0'   # 화면 표시용 텍스트
        self._result = None        # 직전 계산 결과
        self._operator = None      # 현재 선택된 연산자
        self._operand = None       # 첫 번째 피연산자
        self._wait_for_operand = False  # 연산자 직후 새 숫자 입력 대기
        self._init_ui()

    # ── UI 초기화 ──────────────────────────────────────────

    def _init_ui(self):
        self.setWindowTitle('Calculator')
        self.setFixedSize(340, 540)
        self.setStyleSheet('background-color: #000000;')

        layout = QVBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(10, 10, 10, 10)

        # 디스플레이
        self._display = QLabel('0')
        self._display.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self._display.setStyleSheet(
            'color: white;'
            'font-size: 48px;'
            'font-family: Helvetica, Arial;'
            'padding: 10px 15px;'
            'min-height: 80px;'
        )
        layout.addWidget(self._display)

        # 버튼 그리드
        grid = QGridLayout()
        grid.setSpacing(8)

        # 아이폰 계산기 버튼 배치 (행 우선)
        buttons = [
            ('AC', 0, 0, 'func'), ('+/-', 0, 1, 'func'), ('%', 0, 2, 'func'), ('÷', 0, 3, 'op'),
            ('7', 1, 0, 'num'),   ('8', 1, 1, 'num'),     ('9', 1, 2, 'num'),  ('×', 1, 3, 'op'),
            ('4', 2, 0, 'num'),   ('5', 2, 1, 'num'),     ('6', 2, 2, 'num'),  ('−', 2, 3, 'op'),
            ('1', 3, 0, 'num'),   ('2', 3, 1, 'num'),     ('3', 3, 2, 'num'),  ('+', 3, 3, 'op'),
            ('0', 4, 0, 'num'),   ('.', 4, 2, 'num'),     ('=', 4, 3, 'op'),
        ]

        for item in buttons:
            text, row, col = item[0], item[1], item[2]
            btn_type = item[3]

            btn = QPushButton(text)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setMinimumHeight(65)

            # 0 버튼은 2칸 차지
            colspan = 2 if text == '0' else 1

            # 스타일 적용
            style = self._get_button_style(btn_type)
            btn.setStyleSheet(style)

            btn.clicked.connect(self._make_handler(text))
            grid.addWidget(btn, row, col, 1, colspan)

        layout.addLayout(grid)
        self.setLayout(layout)

    # ── 버튼 스타일 ────────────────────────────────────────

    @staticmethod
    def _get_button_style(btn_type):
        '''버튼 종류에 따른 스타일 반환'''
        base = (
            'font-size: 24px;'
            'border-radius: 32px;'
            'border: none;'
        )
        if btn_type == 'num':
            return base + 'background-color: #333333; color: white;'
        if btn_type == 'op':
            return base + 'background-color: #FF9500; color: white;'
        # func (AC, +/-, %)
        return base + 'background-color: #A5A5A5; color: black;'

    # ── 이벤트 핸들러 ──────────────────────────────────────

    def _make_handler(self, text):
        '''버튼 텍스트에 맞는 클릭 핸들러 반환'''
        def handler():
            self._on_button_click(text)
        return handler

    def _on_button_click(self, text):
        '''버튼 클릭 처리'''
        if text.isdigit():
            self._input_digit(text)
        elif text == '.':
            self._input_dot()
        elif text == 'AC':
            self._clear()
        elif text == '+/-':
            self._toggle_sign()
        elif text == '%':
            self._percent()
        elif text == '=':
            self._calculate()
        elif text in ('+', '−', '×', '÷'):
            self._input_operator(text)

    def _update_display(self):
        '''디스플레이 갱신'''
        self._display.setText(self._display_text)

    # ── 숫자 / 소수점 입력 ──────────────────────────────────

    def _input_digit(self, digit):
        if self._wait_for_operand:
            self._display_text = digit
            self._wait_for_operand = False
        else:
            if self._display_text == '0':
                self._display_text = digit
            else:
                self._display_text += digit
        self._update_display()

    def _input_dot(self):
        if self._wait_for_operand:
            self._display_text = '0.'
            self._wait_for_operand = False
        elif '.' not in self._display_text:
            self._display_text += '.'
        self._update_display()

    # ── 기능 버튼 ──────────────────────────────────────────

    def _clear(self):
        self._display_text = '0'
        self._operator = None
        self._operand = None
        self._wait_for_operand = False
        self._update_display()

    def _toggle_sign(self):
        value = float(self._display_text)
        value = -value
        self._display_text = self._format_number(value)
        self._update_display()

    def _percent(self):
        value = float(self._display_text)
        value = value / 100
        self._display_text = self._format_number(value)
        self._update_display()

    # ── 연산자 / 계산 ──────────────────────────────────────

    def _input_operator(self, op):
        current = float(self._display_text)

        # 이전 연산이 있으면 먼저 계산
        if self._operator and not self._wait_for_operand:
            result = self._do_math(self._operand, current, self._operator)
            if result is not None:
                self._display_text = self._format_number(result)
                self._update_display()
                self._operand = result
            else:
                self._display_text = 'Error'
                self._update_display()
                self._operator = None
                self._operand = None
                self._wait_for_operand = True
                return
        else:
            self._operand = current

        self._operator = op
        self._wait_for_operand = True

    def _calculate(self):
        if self._operator is None:
            return
        current = float(self._display_text)
        result = self._do_math(self._operand, current, self._operator)
        if result is not None:
            self._display_text = self._format_number(result)
        else:
            self._display_text = 'Error'
        self._operator = None
        self._operand = None
        self._wait_for_operand = True
        self._update_display()

    @staticmethod
    def _do_math(a, b, op):
        '''4칙연산 수행'''
        if op == '+':
            return a + b
        if op == '−':
            return a - b
        if op == '×':
            return a * b
        if op == '÷':
            if b == 0:
                return None
            return a / b
        return None

    @staticmethod
    def _format_number(value):
        '''숫자를 깔끔한 문자열로 변환'''
        if value == int(value):
            return str(int(value))
        return str(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
