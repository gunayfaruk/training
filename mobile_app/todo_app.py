"""
Mobil Yapılacaklar Listesi Uygulaması
=====================================
Kivy framework kullanılarak geliştirilmiş çapraz platform mobil uygulama.
Android, iOS, Windows, macOS ve Linux üzerinde çalışır.

Özellikler:
- Görev ekleme ve silme
- Görevleri tamamlandı olarak işaretleme
- Görevleri kategorilere ayırma
- Güzel ve modern kullanıcı arayüzü
- Veriler yerel olarak saklanır
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
import json
import os
from datetime import datetime


# Renk teması
COLORS = {
    'primary': (0.2, 0.6, 0.86, 1),      # Mavi
    'primary_dark': (0.15, 0.45, 0.65, 1),
    'secondary': (0.98, 0.4, 0.4, 1),    # Kırmızı
    'success': (0.3, 0.8, 0.4, 1),       # Yeşil
    'warning': (1, 0.75, 0.25, 1),       # Sarı
    'background': (0.95, 0.95, 0.97, 1), # Açık gri
    'card': (1, 1, 1, 1),                # Beyaz
    'text': (0.2, 0.2, 0.2, 1),          # Koyu gri
    'text_light': (0.5, 0.5, 0.5, 1),    # Açık gri metin
}

# Kategori renkleri
CATEGORY_COLORS = {
    'İş': (0.2, 0.6, 0.86, 1),
    'Kişisel': (0.3, 0.8, 0.4, 1),
    'Alışveriş': (1, 0.75, 0.25, 1),
    'Sağlık': (0.98, 0.4, 0.4, 1),
    'Eğitim': (0.6, 0.4, 0.8, 1),
    'Diğer': (0.5, 0.5, 0.5, 1),
}


class TodoItem(BoxLayout):
    """Tek bir yapılacak öğesini temsil eden widget."""

    def __init__(self, todo_data, app_reference, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)
        self.todo_data = todo_data
        self.app_ref = app_reference

        # Arka plan
        with self.canvas.before:
            Color(*COLORS['card'])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Checkbox
        checkbox_layout = BoxLayout(size_hint_x=0.1)
        self.checkbox = CheckBox(active=todo_data.get('completed', False))
        self.checkbox.bind(active=self.on_checkbox_active)
        checkbox_layout.add_widget(self.checkbox)
        self.add_widget(checkbox_layout)

        # Görev bilgileri
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)

        # Görev adı
        self.task_label = Label(
            text=todo_data['task'],
            color=COLORS['text'] if not todo_data.get('completed') else COLORS['text_light'],
            halign='left',
            valign='middle',
            font_size=dp(16),
            bold=True
        )
        self.task_label.bind(size=self.task_label.setter('text_size'))
        info_layout.add_widget(self.task_label)

        # Kategori ve tarih
        category = todo_data.get('category', 'Diğer')
        date_str = todo_data.get('created_at', '')[:10]
        meta_text = f"[color=#808080]{category} • {date_str}[/color]"
        meta_label = Label(
            text=meta_text,
            markup=True,
            halign='left',
            valign='middle',
            font_size=dp(12)
        )
        meta_label.bind(size=meta_label.setter('text_size'))
        info_layout.add_widget(meta_label)

        self.add_widget(info_layout)

        # Kategori renk göstergesi
        category_color = CATEGORY_COLORS.get(category, COLORS['text_light'])
        color_indicator = BoxLayout(size_hint_x=0.05)
        with color_indicator.canvas.before:
            Color(*category_color)
            self.color_rect = RoundedRectangle(
                pos=color_indicator.pos,
                size=(dp(5), dp(40)),
                radius=[dp(2)]
            )
        color_indicator.bind(pos=self._update_color_rect, size=self._update_color_rect)
        self.add_widget(color_indicator)

        # Silme butonu
        delete_btn = Button(
            text='🗑️',
            size_hint_x=0.15,
            background_color=(0, 0, 0, 0),
            font_size=dp(20)
        )
        delete_btn.bind(on_press=self.delete_task)
        self.add_widget(delete_btn)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update_color_rect(self, instance, value):
        self.color_rect.pos = (instance.x + instance.width/2 - dp(2.5), instance.y + dp(15))
        self.color_rect.size = (dp(5), dp(40))

    def on_checkbox_active(self, checkbox, value):
        """Checkbox durumu değiştiğinde çağrılır."""
        self.todo_data['completed'] = value
        self.task_label.color = COLORS['text_light'] if value else COLORS['text']
        self.app_ref.save_todos()

    def delete_task(self, instance):
        """Görevi siler."""
        self.app_ref.delete_todo(self.todo_data)


class AddTodoPopup(Popup):
    """Yeni görev ekleme popup'ı."""

    def __init__(self, app_reference, **kwargs):
        super().__init__(**kwargs)
        self.app_ref = app_reference
        self.title = 'Yeni Görev Ekle'
        self.size_hint = (0.9, 0.5)

        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))

        # Görev adı girişi
        self.task_input = TextInput(
            hint_text='Görev adını girin...',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            padding=[dp(15), dp(15)]
        )
        content.add_widget(self.task_input)

        # Kategori seçimi
        category_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        category_label = Label(
            text='Kategori:',
            size_hint_x=0.3,
            color=COLORS['text']
        )
        category_layout.add_widget(category_label)

        self.category_spinner = Spinner(
            text='Diğer',
            values=list(CATEGORY_COLORS.keys()),
            size_hint_x=0.7
        )
        category_layout.add_widget(self.category_spinner)
        content.add_widget(category_layout)

        # Boşluk
        content.add_widget(BoxLayout())

        # Butonlar
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        cancel_btn = Button(
            text='İptal',
            background_color=COLORS['secondary']
        )
        cancel_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_btn)

        add_btn = Button(
            text='Ekle',
            background_color=COLORS['primary']
        )
        add_btn.bind(on_press=self.add_todo)
        button_layout.add_widget(add_btn)

        content.add_widget(button_layout)
        self.content = content

    def add_todo(self, instance):
        """Yeni görev ekler."""
        task = self.task_input.text.strip()
        if task:
            todo = {
                'task': task,
                'category': self.category_spinner.text,
                'completed': False,
                'created_at': datetime.now().isoformat()
            }
            self.app_ref.add_todo(todo)
            self.dismiss()


class MainScreen(BoxLayout):
    """Ana ekran widget'ı."""

    def __init__(self, app_reference, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.app_ref = app_reference

        # Arka plan rengi
        with self.canvas.before:
            Color(*COLORS['background'])
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Başlık çubuğu
        header = BoxLayout(
            size_hint_y=None,
            height=dp(80),
            padding=[dp(20), dp(10)]
        )
        with header.canvas.before:
            Color(*COLORS['primary'])
            self.header_rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=self._update_header, size=self._update_header)

        title = Label(
            text='📋 Yapılacaklar',
            font_size=dp(24),
            bold=True,
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)

        self.add_widget(header)

        # İstatistik çubuğu
        self.stats_bar = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=[dp(20), dp(10)]
        )
        self.stats_label = Label(
            text='',
            color=COLORS['text'],
            font_size=dp(14)
        )
        self.stats_bar.add_widget(self.stats_label)
        self.add_widget(self.stats_bar)

        # Görev listesi (ScrollView içinde)
        scroll_view = ScrollView()
        self.todo_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=[dp(15), dp(10)]
        )
        self.todo_list.bind(minimum_height=self.todo_list.setter('height'))
        scroll_view.add_widget(self.todo_list)
        self.add_widget(scroll_view)

        # Alt çubuk - Ekle butonu
        footer = BoxLayout(
            size_hint_y=None,
            height=dp(80),
            padding=[dp(20), dp(15)]
        )

        add_button = Button(
            text='+ Yeni Görev Ekle',
            font_size=dp(18),
            background_color=COLORS['primary'],
            bold=True
        )
        add_button.bind(on_press=self.show_add_popup)
        footer.add_widget(add_button)

        self.add_widget(footer)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update_header(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def show_add_popup(self, instance):
        """Yeni görev ekleme popup'ını gösterir."""
        popup = AddTodoPopup(self.app_ref)
        popup.open()

    def update_stats(self, todos):
        """İstatistikleri günceller."""
        total = len(todos)
        completed = sum(1 for t in todos if t.get('completed', False))
        pending = total - completed
        self.stats_label.text = f'📊 Toplam: {total} | ✅ Tamamlanan: {completed} | ⏳ Bekleyen: {pending}'

    def refresh_todo_list(self, todos):
        """Görev listesini yeniler."""
        self.todo_list.clear_widgets()

        # Önce tamamlanmamış, sonra tamamlanmış görevler
        sorted_todos = sorted(todos, key=lambda x: (x.get('completed', False), x.get('created_at', '')))

        for todo in sorted_todos:
            item = TodoItem(todo, self.app_ref)
            self.todo_list.add_widget(item)

        self.update_stats(todos)


class TodoApp(App):
    """Ana uygulama sınıfı."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.todos = []
        self.data_file = 'todos.json'

    def build(self):
        """Uygulamayı oluşturur."""
        self.title = 'Yapılacaklar Listesi'

        # Pencere boyutunu mobil için ayarla
        Window.size = (400, 700)

        # Ana ekranı oluştur
        self.main_screen = MainScreen(self)

        # Kayıtlı görevleri yükle
        self.load_todos()

        return self.main_screen

    def load_todos(self):
        """Görevleri dosyadan yükler."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.todos = json.load(f)
        except (json.JSONDecodeError, IOError):
            self.todos = []

        self.main_screen.refresh_todo_list(self.todos)

    def save_todos(self):
        """Görevleri dosyaya kaydeder."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Kaydetme hatası: {e}")

    def add_todo(self, todo):
        """Yeni görev ekler."""
        self.todos.append(todo)
        self.save_todos()
        self.main_screen.refresh_todo_list(self.todos)

    def delete_todo(self, todo):
        """Görevi siler."""
        if todo in self.todos:
            self.todos.remove(todo)
            self.save_todos()
            self.main_screen.refresh_todo_list(self.todos)


def main():
    """Uygulamayı başlatır."""
    print("=" * 50)
    print("📱 Mobil Yapılacaklar Listesi Uygulaması")
    print("=" * 50)
    print("\nUygulama başlatılıyor...")
    print("Bu uygulama Kivy framework ile geliştirilmiştir.")
    print("Android ve iOS için derlenebilir.\n")

    TodoApp().run()


if __name__ == '__main__':
    main()
