"""
Python Çoklu Kalıtım (Multiple Inheritance) Örneği
Bu dosya doğru ve yanlış kullanım örneklerini gösterir.
"""

print("=" * 60)
print("YANLIŞ KULLANIM - __init__ None döndürür")
print("=" * 60)

class UstSinif1_Yanlis:
    def __init__(self, p):
        print("Ustsinif1 calisti.")
        self.p = p

class UstSinif2_Yanlis:
    def __init__(self, t):
        print("Ustsinif2 calisti.")
        self.t = t

class AltSinif_Yanlis(UstSinif1_Yanlis, UstSinif2_Yanlis):
    def __init__(self, a, b):
        # PROBLEM: __init__ None döndürür, self.a ve self.b None olur
        self.a = UstSinif1_Yanlis.__init__(self, a)
        self.b = UstSinif2_Yanlis.__init__(self, b)

A = AltSinif_Yanlis("a", "b")
print(f"self.a değeri: {A.a}")  # None
print(f"self.b değeri: {A.b}")  # None
print(f"self.p değeri: {A.p}")  # "a"
print(f"self.t değeri: {A.t}")  # "b"

print("\n" + "=" * 60)
print("DOĞRU KULLANIM 1 - Direkt çağırma")
print("=" * 60)

class UstSinif1:
    def __init__(self, p):
        print("Ustsinif1 calisti.")
        self.p = p

class UstSinif2:
    def __init__(self, t):
        print("Ustsinif2 calisti.")
        self.t = t

class AltSinif_Duzeltilmis(UstSinif1, UstSinif2):
    def __init__(self, a, b):
        # Doğru: Sadece çağırıyoruz, atama yapmıyoruz
        UstSinif1.__init__(self, a)
        UstSinif2.__init__(self, b)
        # Artık self.p ve self.t değerleri ayarlandı

B = AltSinif_Duzeltilmis("a", "b")
print(f"self.p değeri: {B.p}")  # "a"
print(f"self.t değeri: {B.t}")  # "b"

print("\n" + "=" * 60)
print("DOĞRU KULLANIM 2 - super() ile (ÖNERİLEN)")
print("=" * 60)

class UstSinif1_Super:
    def __init__(self, p, **kwargs):
        print("Ustsinif1 calisti.")
        self.p = p
        super().__init__(**kwargs)  # MRO zincirinde sonraki sınıfı çağır

class UstSinif2_Super:
    def __init__(self, t, **kwargs):
        print("Ustsinif2 calisti.")
        self.t = t
        super().__init__(**kwargs)  # MRO zincirinde sonraki sınıfı çağır

class AltSinif_Super(UstSinif1_Super, UstSinif2_Super):
    def __init__(self, a, b):
        # super() kullanarak MRO (Method Resolution Order) takip edilir
        # **kwargs ile parametreler zincir boyunca iletilir
        super().__init__(p=a, t=b)
        print("AltSinif_Super __init__ tamamlandi")

C = AltSinif_Super("a", "b")
print(f"self.p değeri: {C.p}")  # "a"
print(f"self.t değeri: {C.t}")  # "b"

print("\n" + "=" * 60)
print("DOĞRU KULLANIM 3 - Pratik Örnek")
print("=" * 60)

class Personel:
    def __init__(self, ad, soyad):
        self.ad = ad
        self.soyad = soyad
        print(f"Personel oluşturuldu: {ad} {soyad}")

class Departman:
    def __init__(self, departman_adi):
        self.departman_adi = departman_adi
        print(f"Departman: {departman_adi}")

class Calisan(Personel, Departman):
    def __init__(self, ad, soyad, departman, maas):
        Personel.__init__(self, ad, soyad)
        Departman.__init__(self, departman)
        self.maas = maas

    def bilgileri_goster(self):
        return f"{self.ad} {self.soyad} - {self.departman_adi} - {self.maas} TL"

calisan = Calisan("Ahmet", "Yılmaz", "Yazılım", 15000)
print(calisan.bilgileri_goster())

print("\n" + "=" * 60)
print("MRO (Method Resolution Order) - Metod Çözümleme Sırası")
print("=" * 60)
print("AltSinif_Super MRO:", AltSinif_Super.__mro__)
