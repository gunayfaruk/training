"""
Not Defteri Uygulaması - Çoklu Kalıtım Örneği
Bu uygulama Note, NoteManager ve Storage sınıflarını kullanarak
çoklu kalıtım yapısını gösterir.
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
import uuid


# ============================================================
# 1. NOTE SINIFI - Not nesneleri için
# ============================================================

class Note:
    """Bir not nesnesi oluşturur ve yönetir"""

    def __init__(self, baslik: str, icerik: str, yazar: str, id: Optional[str] = None):
        self.id = id or str(uuid.uuid4())  # Benzersiz ID
        self.baslik = baslik
        self.icerik = icerik
        self.yazar = yazar
        self.olusturulma_tarihi = datetime.now()
        self.guncellenme_tarihi = datetime.now()

    def guncelle(self, baslik: Optional[str] = None, icerik: Optional[str] = None):
        """Not içeriğini günceller"""
        if baslik:
            self.baslik = baslik
        if icerik:
            self.icerik = icerik
        self.guncellenme_tarihi = datetime.now()

    def to_dict(self) -> Dict:
        """Not nesnesini sözlük formatına dönüştürür"""
        return {
            'id': self.id,
            'baslik': self.baslik,
            'icerik': self.icerik,
            'yazar': self.yazar,
            'olusturulma_tarihi': self.olusturulma_tarihi.isoformat(),
            'guncellenme_tarihi': self.guncellenme_tarihi.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Note':
        """Sözlükten Note nesnesi oluşturur"""
        note = cls(
            baslik=data['baslik'],
            icerik=data['icerik'],
            yazar=data['yazar'],
            id=data['id']
        )
        note.olusturulma_tarihi = datetime.fromisoformat(data['olusturulma_tarihi'])
        note.guncellenme_tarihi = datetime.fromisoformat(data['guncellenme_tarihi'])
        return note

    def __str__(self) -> str:
        return f"[{self.id[:8]}] {self.baslik} - {self.yazar} ({self.olusturulma_tarihi.strftime('%Y-%m-%d %H:%M')})"

    def __repr__(self) -> str:
        return f"Note(id='{self.id[:8]}...', baslik='{self.baslik}')"


# ============================================================
# 2. NOTEMANAGER SINIFI - Not yönetimi için
# ============================================================

class NoteManager:
    """Notları yönetir: arama, değiştirme, silme"""

    def __init__(self):
        self.notlar: List[Note] = []

    def not_ekle(self, note: Note):
        """Yeni not ekler"""
        self.notlar.append(note)
        print(f"✓ Not eklendi: {note.baslik}")

    def not_ara(self, arama_terimi: str) -> List[Note]:
        """
        Başlık, içerik veya yazar içinde arama yapar
        """
        sonuclar = []
        arama_terimi = arama_terimi.lower()

        for note in self.notlar:
            if (arama_terimi in note.baslik.lower() or
                arama_terimi in note.icerik.lower() or
                arama_terimi in note.yazar.lower()):
                sonuclar.append(note)

        return sonuclar

    def not_ara_id(self, note_id: str) -> Optional[Note]:
        """ID ile not arar"""
        for note in self.notlar:
            if note.id == note_id or note.id.startswith(note_id):
                return note
        return None

    def not_degistir(self, note_id: str, baslik: Optional[str] = None,
                     icerik: Optional[str] = None) -> bool:
        """Var olan bir notu günceller"""
        note = self.not_ara_id(note_id)
        if note:
            note.guncelle(baslik, icerik)
            print(f"✓ Not güncellendi: {note.baslik}")
            return True
        else:
            print(f"✗ Not bulunamadı: {note_id}")
            return False

    def not_sil(self, note_id: str) -> bool:
        """ID'ye göre not siler"""
        note = self.not_ara_id(note_id)
        if note:
            self.notlar.remove(note)
            print(f"✓ Not silindi: {note.baslik}")
            return True
        else:
            print(f"✗ Not bulunamadı: {note_id}")
            return False

    def tum_notlari_listele(self):
        """Tüm notları listeler"""
        if not self.notlar:
            print("Henüz not eklenmemiş.")
            return

        print(f"\n{'='*60}")
        print(f"TOPLAM {len(self.notlar)} NOT")
        print(f"{'='*60}")
        for i, note in enumerate(self.notlar, 1):
            print(f"{i}. {note}")


# ============================================================
# 3. STORAGE SINIFI - Kayıt formatları
# ============================================================

class Storage:
    """Notları farklı formatlarda kaydeder: text, json, sqlite"""

    def __init__(self, kayit_formati: str = "json"):
        self.kayit_formati = kayit_formati

    def text_kaydet(self, notlar: List[Note], dosya_adi: str = "notlar.txt"):
        """Notları text formatında kaydeder"""
        with open(dosya_adi, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("NOT DEFTERİ - TEXT FORMAT\n")
            f.write("=" * 60 + "\n\n")

            for i, note in enumerate(notlar, 1):
                f.write(f"NOT #{i}\n")
                f.write(f"ID: {note.id}\n")
                f.write(f"Başlık: {note.baslik}\n")
                f.write(f"Yazar: {note.yazar}\n")
                f.write(f"Oluşturulma: {note.olusturulma_tarihi.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Güncellenme: {note.guncellenme_tarihi.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"İçerik:\n{note.icerik}\n")
                f.write("-" * 60 + "\n\n")

        print(f"✓ Notlar text formatında kaydedildi: {dosya_adi}")

    def json_kaydet(self, notlar: List[Note], dosya_adi: str = "notlar.json"):
        """Notları JSON formatında kaydeder"""
        data = {
            'notlar': [note.to_dict() for note in notlar],
            'toplam': len(notlar),
            'kayit_tarihi': datetime.now().isoformat()
        }

        with open(dosya_adi, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ Notlar JSON formatında kaydedildi: {dosya_adi}")

    def json_yukle(self, dosya_adi: str = "notlar.json") -> List[Note]:
        """JSON dosyasından notları yükler"""
        try:
            with open(dosya_adi, 'r', encoding='utf-8') as f:
                data = json.load(f)

            notlar = [Note.from_dict(note_data) for note_data in data['notlar']]
            print(f"✓ {len(notlar)} not JSON'dan yüklendi: {dosya_adi}")
            return notlar
        except FileNotFoundError:
            print(f"✗ Dosya bulunamadı: {dosya_adi}")
            return []

    def sqlite_kaydet(self, notlar: List[Note], veritabani: str = "notlar.db"):
        """Notları SQLite veritabanına kaydeder"""
        conn = sqlite3.connect(veritabani)
        cursor = conn.cursor()

        # Tablo oluştur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notlar (
                id TEXT PRIMARY KEY,
                baslik TEXT NOT NULL,
                icerik TEXT NOT NULL,
                yazar TEXT NOT NULL,
                olusturulma_tarihi TEXT NOT NULL,
                guncellenme_tarihi TEXT NOT NULL
            )
        ''')

        # Eski verileri temizle
        cursor.execute('DELETE FROM notlar')

        # Notları ekle
        for note in notlar:
            cursor.execute('''
                INSERT INTO notlar VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                note.id,
                note.baslik,
                note.icerik,
                note.yazar,
                note.olusturulma_tarihi.isoformat(),
                note.guncellenme_tarihi.isoformat()
            ))

        conn.commit()
        conn.close()
        print(f"✓ {len(notlar)} not SQLite veritabanına kaydedildi: {veritabani}")

    def sqlite_yukle(self, veritabani: str = "notlar.db") -> List[Note]:
        """SQLite veritabanından notları yükler"""
        try:
            conn = sqlite3.connect(veritabani)
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM notlar')
            rows = cursor.fetchall()

            notlar = []
            for row in rows:
                note_data = {
                    'id': row[0],
                    'baslik': row[1],
                    'icerik': row[2],
                    'yazar': row[3],
                    'olusturulma_tarihi': row[4],
                    'guncellenme_tarihi': row[5]
                }
                notlar.append(Note.from_dict(note_data))

            conn.close()
            print(f"✓ {len(notlar)} not SQLite'dan yüklendi: {veritabani}")
            return notlar
        except sqlite3.OperationalError:
            print(f"✗ Veritabanı bulunamadı veya tablo yok: {veritabani}")
            return []


# ============================================================
# 4. NOTEBOOKAPP - ÇOKLU KALITIM KULLANAN ANA SINIF
# ============================================================

class NotebookApp(NoteManager, Storage):
    """
    Çoklu kalıtım örneği: NoteManager ve Storage sınıflarından kalıtım alır

    MRO (Method Resolution Order): NotebookApp -> NoteManager -> Storage -> object
    """

    def __init__(self, kayit_formati: str = "json"):
        # Her iki parent sınıfın __init__ metodunu çağır
        NoteManager.__init__(self)
        Storage.__init__(self, kayit_formati)
        print(f"NotebookApp başlatıldı (Format: {kayit_formati})")

    def kaydet(self, dosya_adi: Optional[str] = None):
        """Notları belirlenen formatta kaydeder"""
        if not dosya_adi:
            if self.kayit_formati == "text":
                dosya_adi = "notlar.txt"
            elif self.kayit_formati == "json":
                dosya_adi = "notlar.json"
            elif self.kayit_formati == "sqlite":
                dosya_adi = "notlar.db"

        if self.kayit_formati == "text":
            self.text_kaydet(self.notlar, dosya_adi)
        elif self.kayit_formati == "json":
            self.json_kaydet(self.notlar, dosya_adi)
        elif self.kayit_formati == "sqlite":
            self.sqlite_kaydet(self.notlar, dosya_adi)

    def yukle(self, dosya_adi: Optional[str] = None):
        """Notları belirlenen formattan yükler"""
        if not dosya_adi:
            if self.kayit_formati == "json":
                dosya_adi = "notlar.json"
            elif self.kayit_formati == "sqlite":
                dosya_adi = "notlar.db"

        if self.kayit_formati == "json":
            self.notlar = self.json_yukle(dosya_adi)
        elif self.kayit_formati == "sqlite":
            self.notlar = self.sqlite_yukle(dosya_adi)

    def format_degistir(self, yeni_format: str):
        """Kayıt formatını değiştirir"""
        if yeni_format in ["text", "json", "sqlite"]:
            self.kayit_formati = yeni_format
            print(f"✓ Kayıt formatı değiştirildi: {yeni_format}")
        else:
            print(f"✗ Geçersiz format: {yeni_format}")


# ============================================================
# 5. ÖRNEK KULLANIM VE DEMO
# ============================================================

def demo():
    """Uygulamanın demo kullanımı"""

    print("\n" + "=" * 60)
    print("NOT DEFTERİ UYGULAMASI - ÇOKLU KALITIM DEMO")
    print("=" * 60 + "\n")

    # NotebookApp oluştur (çoklu kalıtım kullanıyor)
    print("1. UYGULAMA BAŞLATMA")
    print("-" * 60)
    app = NotebookApp(kayit_formati="json")

    # MRO (Method Resolution Order) göster
    print(f"\nMRO: {' -> '.join([cls.__name__ for cls in NotebookApp.__mro__])}")

    # Notlar ekle
    print("\n2. NOT EKLEME")
    print("-" * 60)
    note1 = Note("Python Öğreniyorum", "Python'da çoklu kalıtım çok faydalı!", "Ahmet")
    note2 = Note("Django Projesi", "REST API geliştirmeye başladım", "Ayşe")
    note3 = Note("Alışveriş Listesi", "Ekmek, süt, yumurta al", "Mehmet")
    note4 = Note("Python İleri Seviye", "Decoratorlar ve metasınıflar", "Ahmet")

    app.not_ekle(note1)
    app.not_ekle(note2)
    app.not_ekle(note3)
    app.not_ekle(note4)

    # Tüm notları listele
    print("\n3. TÜM NOTLARI LİSTELE")
    print("-" * 60)
    app.tum_notlari_listele()

    # Not arama
    print("\n4. NOT ARAMA")
    print("-" * 60)
    print("Arama: 'Python'")
    sonuclar = app.not_ara("Python")
    for note in sonuclar:
        print(f"  - {note}")

    print("\nArama: 'Ahmet'")
    sonuclar = app.not_ara("Ahmet")
    for note in sonuclar:
        print(f"  - {note}")

    # Not güncelleme
    print("\n5. NOT GÜNCELLEME")
    print("-" * 60)
    if app.notlar:
        ilk_not_id = app.notlar[0].id
        app.not_degistir(ilk_not_id, icerik="Python'da çoklu kalıtım ve MRO çok önemli!")

    # JSON formatında kaydet
    print("\n6. JSON FORMATINDA KAYDETME")
    print("-" * 60)
    app.kaydet("demo_notlar.json")

    # Text formatında kaydet
    print("\n7. TEXT FORMATINDA KAYDETME")
    print("-" * 60)
    app.format_degistir("text")
    app.kaydet("demo_notlar.txt")

    # SQLite formatında kaydet
    print("\n8. SQLITE FORMATINDA KAYDETME")
    print("-" * 60)
    app.format_degistir("sqlite")
    app.kaydet("demo_notlar.db")

    # Yeni uygulama oluştur ve JSON'dan yükle
    print("\n9. JSON'DAN YÜKLEME")
    print("-" * 60)
    app2 = NotebookApp(kayit_formati="json")
    app2.yukle("demo_notlar.json")
    app2.tum_notlari_listele()

    # Not silme
    print("\n10. NOT SILME")
    print("-" * 60)
    if app2.notlar:
        son_not_id = app2.notlar[-1].id
        app2.not_sil(son_not_id)
    app2.tum_notlari_listele()

    print("\n" + "=" * 60)
    print("DEMO TAMAMLANDI!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
