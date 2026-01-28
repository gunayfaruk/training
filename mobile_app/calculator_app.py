"""
Mobil Hesap Makinesi Uygulaması
================================
Kivy framework kullanılarak geliştirilmiş modern hesap makinesi.
Android, iOS, Windows, macOS ve Linux üzerinde çalışır.

Özellikler:
- Temel matematiksel işlemler (+, -, *, /)
- Yüzde hesaplama
- Ondalık sayılar
- Geçmiş silme ve sıfırlama
- Modern ve kullanıcı dostu arayüz
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp


# Renk teması
COLORS = {
    'background': (0.12, 0.12, 0.14, 1),     # Koyu arka plan
    'display_bg': (0.18, 0.18, 0.2, 1),      # Ekran arka planı
    'number': (0.25, 0.25, 0.28, 1),         # Sayı butonları
    'operator': (1, 0.62, 0.04, 1),          # Operatör butonları (turuncu)
    'function': (0.4, 0.4, 0.42, 1),         # Fonksiyon butonları
    'text': (1, 1, 1, 1),                    # Beyaz metin
    'text_dark': (0, 0, 0, 1),               # Siyah metin
}


class CalculatorButton(Button):
    """Özelleştirilmiş hesap makinesi butonu."""

    def __init__(self, text, btn_type='number', **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = dp(28)
        self.bold = True

        # Buton tipine göre renk ayarla
        if btn_type == 'operator':
            self.background_color = COLORS['operator']
            self.color = COLORS['text']
        elif btn_type == 'function':
            self.background_color = COLORS['function']
            self.color = COLORS['text']
        elif btn_type == 'equal':
            self.background_color = COLORS['operator']
            self.color = COLORS['text']
        else:  # number
            self.background_color = COLORS['number']
            self.color = COLORS['text']


class DisplayLabel(Label):
    """Hesap makinesi ekranı."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = '0'
        self.font_size = dp(48)
        self.halign = 'right'
        self.valign = 'bottom'
        self.padding = [dp(20), dp(20)]
        self.color = COLORS['text']
        self.bind(size=self.setter('text_size'))


class CalculatorApp(App):
    """Ana hesap makinesi uygulaması."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current = '0'
        self.previous = ''
        self.operation = ''
        self.should_reset = False

    def build(self):
        """Uygulamayı oluşturur."""
        self.title = 'Hesap Makinesi'

        # Pencere boyutunu mobil için ayarla
        Window.size = (380, 600)
        Window.clearcolor = COLORS['background']

        # Ana layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Arka plan
        with main_layout.canvas.before:
            Color(*COLORS['background'])
            self.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self._update_bg, size=self._update_bg)

        # Ekran alanı
        display_layout = BoxLayout(size_hint_y=0.25)
        with display_layout.canvas.before:
            Color(*COLORS['display_bg'])
            self.display_rect = RoundedRectangle(
                pos=display_layout.pos,
                size=display_layout.size,
                radius=[dp(15)]
            )
        display_layout.bind(pos=self._update_display, size=self._update_display)

        self.display = DisplayLabel()
        display_layout.add_widget(self.display)
        main_layout.add_widget(display_layout)

        # Buton grid'i
        button_grid = GridLayout(
            cols=4,
            spacing=dp(10),
            size_hint_y=0.75
        )

        # Buton düzeni
        buttons = [
            ('C', 'function'), ('±', 'function'), ('%', 'function'), ('÷', 'operator'),
            ('7', 'number'), ('8', 'number'), ('9', 'number'), ('×', 'operator'),
            ('4', 'number'), ('5', 'number'), ('6', 'number'), ('-', 'operator'),
            ('1', 'number'), ('2', 'number'), ('3', 'number'), ('+', 'operator'),
            ('0', 'number'), ('.', 'number'), ('⌫', 'function'), ('=', 'equal'),
        ]

        for btn_text, btn_type in buttons:
            btn = CalculatorButton(btn_text, btn_type)
            btn.bind(on_press=self.on_button_press)
            button_grid.add_widget(btn)

        main_layout.add_widget(button_grid)

        return main_layout

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _update_display(self, instance, value):
        self.display_rect.pos = instance.pos
        self.display_rect.size = instance.size

    def on_button_press(self, instance):
        """Buton basıldığında çağrılır."""
        btn_text = instance.text

        if btn_text.isdigit():
            self.handle_number(btn_text)
        elif btn_text == '.':
            self.handle_decimal()
        elif btn_text in ['+', '-', '×', '÷']:
            self.handle_operator(btn_text)
        elif btn_text == '=':
            self.handle_equal()
        elif btn_text == 'C':
            self.handle_clear()
        elif btn_text == '±':
            self.handle_negate()
        elif btn_text == '%':
            self.handle_percent()
        elif btn_text == '⌫':
            self.handle_backspace()

        self.update_display()

    def handle_number(self, num):
        """Sayı girişi."""
        if self.should_reset:
            self.current = num
            self.should_reset = False
        elif self.current == '0':
            self.current = num
        else:
            if len(self.current) < 12:  # Maksimum karakter sınırı
                self.current += num

    def handle_decimal(self):
        """Ondalık nokta girişi."""
        if self.should_reset:
            self.current = '0.'
            self.should_reset = False
        elif '.' not in self.current:
            self.current += '.'

    def handle_operator(self, op):
        """Operatör girişi."""
        if self.previous and self.operation and not self.should_reset:
            self.handle_equal()

        self.previous = self.current
        self.operation = op
        self.should_reset = True

    def handle_equal(self):
        """Eşittir işlemi."""
        if not self.previous or not self.operation:
            return

        try:
            prev = float(self.previous)
            curr = float(self.current)

            if self.operation == '+':
                result = prev + curr
            elif self.operation == '-':
                result = prev - curr
            elif self.operation == '×':
                result = prev * curr
            elif self.operation == '÷':
                if curr == 0:
                    self.current = 'Hata'
                    self.previous = ''
                    self.operation = ''
                    self.should_reset = True
                    return
                result = prev / curr

            # Sonucu formatla
            if result == int(result):
                self.current = str(int(result))
            else:
                self.current = f'{result:.8g}'

        except (ValueError, OverflowError):
            self.current = 'Hata'

        self.previous = ''
        self.operation = ''
        self.should_reset = True

    def handle_clear(self):
        """Tümünü temizle."""
        self.current = '0'
        self.previous = ''
        self.operation = ''
        self.should_reset = False

    def handle_negate(self):
        """İşaret değiştir."""
        if self.current != '0' and self.current != 'Hata':
            if self.current.startswith('-'):
                self.current = self.current[1:]
            else:
                self.current = '-' + self.current

    def handle_percent(self):
        """Yüzde hesapla."""
        try:
            value = float(self.current)
            result = value / 100
            if result == int(result):
                self.current = str(int(result))
            else:
                self.current = f'{result:.8g}'
        except ValueError:
            self.current = 'Hata'

    def handle_backspace(self):
        """Son karakteri sil."""
        if len(self.current) > 1:
            self.current = self.current[:-1]
        else:
            self.current = '0'

    def update_display(self):
        """Ekranı güncelle."""
        display_text = self.current

        # Operatör göster
        if self.operation and self.should_reset:
            display_text = f'{self.previous} {self.operation}'

        self.display.text = display_text


def main():
    """Uygulamayı başlatır."""
    print("=" * 50)
    print("🧮 Mobil Hesap Makinesi Uygulaması")
    print("=" * 50)
    print("\nUygulama başlatılıyor...")
    print("Bu uygulama Kivy framework ile geliştirilmiştir.")
    print("Android ve iOS için derlenebilir.\n")

    CalculatorApp().run()


if __name__ == '__main__':
    main()
