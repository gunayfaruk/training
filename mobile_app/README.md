# Mobil Uygulamalar

Bu klasör Kivy framework kullanılarak geliştirilmiş çapraz platform mobil uygulamaları içerir.

## Uygulamalar

### 1. Yapılacaklar Listesi (`todo_app.py`)
Modern ve kullanıcı dostu bir yapılacaklar listesi uygulaması.

**Özellikler:**
- Görev ekleme ve silme
- Görevleri tamamlandı olarak işaretleme
- Kategorilere göre gruplama (İş, Kişisel, Alışveriş, Sağlık, Eğitim)
- İstatistik görüntüleme
- Yerel veri saklama (JSON)

### 2. Hesap Makinesi (`calculator_app.py`)
Şık tasarımlı hesap makinesi uygulaması.

**Özellikler:**
- Temel matematiksel işlemler (+, -, ×, ÷)
- Yüzde hesaplama
- İşaret değiştirme
- Ondalık sayı desteği
- Modern koyu tema

## Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Yapılacaklar uygulamasını çalıştır
python todo_app.py

# Hesap makinesini çalıştır
python calculator_app.py
```

## Android APK Oluşturma

```bash
# Buildozer'ı yükle
pip install buildozer

# APK oluştur
buildozer android debug

# APK dosyası bin/ klasöründe oluşturulur
```

## Gereksinimler

- Python 3.8+
- Kivy 2.2.0+

## Platform Desteği

- Android
- iOS
- Windows
- macOS
- Linux
