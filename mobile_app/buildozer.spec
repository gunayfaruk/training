# Buildozer Yapılandırma Dosyası
# ================================
# Bu dosya Android APK oluşturmak için kullanılır
# Kullanım: buildozer android debug

[app]

# Uygulama adı
title = Yapilacaklar Listesi

# Paket adı (benzersiz olmalı)
package.name = todolist

# Paket domain'i
package.domain = com.example

# Kaynak dosyaların bulunduğu dizin
source.dir = .

# Ana Python dosyası
source.include_exts = py,png,jpg,kv,atlas,json

# Uygulama versiyonu
version = 1.0.0

# Gereksinimler
requirements = python3,kivy

# Uygulama ikonu (opsiyonel)
# icon.filename = %(source.dir)s/data/icon.png

# Başlangıç ekranı (opsiyonel)
# presplash.filename = %(source.dir)s/data/presplash.png

# Uygulama yönlendirmesi (portrait, landscape, all)
orientation = portrait

# Android izinleri
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android API seviyesi
android.api = 33
android.minapi = 21

# NDK sürümü
android.ndk = 25b

# Android SDK sürümü
android.sdk = 33

# Tam ekran modu
fullscreen = 0

# Arka plan rengi
android.presplash_color = #FFFFFF

# Uygulama açıklaması
# Türkçe karakterler için encoding kullanılıyor
android.meta_data =

[buildozer]

# Buildozer log seviyesi (0 = hata, 1 = uyarı, 2 = bilgi)
log_level = 2

# Uyarıları göster
warn_on_root = 1

# Build dizini
build_dir = ./.buildozer

# Bin dizini (APK'lar buraya oluşturulur)
bin_dir = ./bin
