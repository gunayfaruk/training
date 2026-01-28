"""
GitLab On-Premise Entegrasyonu

Bu modül, kendi sunucunuzda (on-premise) barındırılan GitLab ile
entegrasyon sağlamak için gerekli sınıfları ve fonksiyonları içerir.

Özellikler:
- Özel GitLab sunucusuna bağlantı
- Token tabanlı kimlik doğrulama
- Proje yönetimi (listeleme, oluşturma, silme)
- Issue yönetimi
- Merge Request işlemleri
- Kullanıcı bilgileri

Gereksinimler:
    pip install python-gitlab requests

Kullanım:
    from gitlab_onprem import GitLabOnPrem

    gitlab = GitLabOnPrem(
        url="https://gitlab.sirketiniz.com",
        private_token="glpat-xxxxx"
    )
    gitlab.baglan()
    projeler = gitlab.projeleri_listele()
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# Not: Gerçek kullanımda python-gitlab kütüphanesi gerekir
# pip install python-gitlab
# Bu örnek, kütüphane olmadan da çalışabilecek şekilde tasarlanmıştır


class GitLabDurumu(Enum):
    """GitLab bağlantı durumları"""
    BAGLI_DEGIL = "bağlı_değil"
    BAGLI = "bağlı"
    HATA = "hata"
    KIMLIK_DOGRULAMA_HATASI = "kimlik_doğrulama_hatası"


@dataclass
class GitLabKullanici:
    """GitLab kullanıcı bilgileri"""
    id: int
    kullanici_adi: str
    ad: str
    email: str
    avatar_url: Optional[str] = None
    web_url: Optional[str] = None

    def __str__(self):
        return f"{self.ad} (@{self.kullanici_adi})"


@dataclass
class GitLabProje:
    """GitLab proje bilgileri"""
    id: int
    ad: str
    aciklama: Optional[str]
    web_url: str
    ssh_url: Optional[str] = None
    http_url: Optional[str] = None
    varsayilan_dal: str = "main"
    gorunurluk: str = "private"
    olusturma_tarihi: Optional[datetime] = None
    son_aktivite: Optional[datetime] = None

    def __str__(self):
        return f"[{self.id}] {self.ad}"


@dataclass
class GitLabIssue:
    """GitLab issue (sorun) bilgileri"""
    id: int
    iid: int  # Proje içi ID
    baslik: str
    aciklama: Optional[str]
    durum: str  # opened, closed
    proje_id: int
    yazar: Optional[GitLabKullanici] = None
    atanan: Optional[GitLabKullanici] = None
    etiketler: List[str] = field(default_factory=list)
    olusturma_tarihi: Optional[datetime] = None

    def __str__(self):
        return f"#{self.iid} - {self.baslik} [{self.durum}]"


@dataclass
class GitLabMergeRequest:
    """GitLab Merge Request bilgileri"""
    id: int
    iid: int
    baslik: str
    aciklama: Optional[str]
    durum: str  # opened, closed, merged
    kaynak_dal: str
    hedef_dal: str
    proje_id: int
    yazar: Optional[GitLabKullanici] = None

    def __str__(self):
        return f"!{self.iid} - {self.baslik} ({self.kaynak_dal} → {self.hedef_dal})"


class GitLabBaglantisi:
    """
    GitLab bağlantı yönetimi için temel sınıf.

    Bu sınıf, GitLab API'sine bağlantı kurma ve
    kimlik doğrulama işlemlerini yönetir.
    """

    def __init__(self, url: str, private_token: Optional[str] = None,
                 oauth_token: Optional[str] = None):
        """
        GitLab bağlantısı oluştur.

        Args:
            url: GitLab sunucu URL'si (örn: https://gitlab.sirketiniz.com)
            private_token: Kişisel erişim token'ı
            oauth_token: OAuth2 token (opsiyonel)
        """
        self.url = url.rstrip('/')
        self.private_token = private_token
        self.oauth_token = oauth_token
        self.durum = GitLabDurumu.BAGLI_DEGIL
        self.kullanici: Optional[GitLabKullanici] = None
        self._gl = None  # python-gitlab instance

    def baglan(self) -> bool:
        """
        GitLab sunucusuna bağlan.

        Returns:
            bool: Bağlantı başarılı ise True
        """
        try:
            # python-gitlab kütüphanesi kurulu ise kullan
            try:
                import gitlab
                self._gl = gitlab.Gitlab(
                    self.url,
                    private_token=self.private_token,
                    oauth_token=self.oauth_token
                )
                self._gl.auth()

                # Mevcut kullanıcı bilgilerini al
                user = self._gl.user
                self.kullanici = GitLabKullanici(
                    id=user.id,
                    kullanici_adi=user.username,
                    ad=user.name,
                    email=user.email,
                    avatar_url=getattr(user, 'avatar_url', None),
                    web_url=getattr(user, 'web_url', None)
                )
                self.durum = GitLabDurumu.BAGLI
                return True

            except ImportError:
                # Kütüphane yoksa simülasyon modu
                print("⚠️  python-gitlab kütüphanesi bulunamadı.")
                print("    Kurulum: pip install python-gitlab")
                print("    Simülasyon modunda devam ediliyor...")
                self._simulasyon_modu = True
                self.durum = GitLabDurumu.BAGLI
                self.kullanici = GitLabKullanici(
                    id=1,
                    kullanici_adi="demo_kullanici",
                    ad="Demo Kullanıcı",
                    email="demo@sirket.com"
                )
                return True

        except Exception as e:
            self.durum = GitLabDurumu.HATA
            print(f"❌ Bağlantı hatası: {e}")
            return False

    def baglanti_kontrol(self) -> bool:
        """Bağlantı durumunu kontrol et."""
        return self.durum == GitLabDurumu.BAGLI

    def baglanti_bilgisi(self) -> Dict[str, Any]:
        """Bağlantı bilgilerini döndür."""
        return {
            "url": self.url,
            "durum": self.durum.value,
            "kullanici": str(self.kullanici) if self.kullanici else None
        }


class GitLabProjeYoneticisi:
    """
    GitLab proje işlemleri için sınıf.

    Proje listeleme, oluşturma, güncelleme ve silme
    işlemlerini gerçekleştirir.
    """

    def __init__(self):
        self._projeler: Dict[int, GitLabProje] = {}

    def projeleri_listele(self, arama: Optional[str] = None,
                          sayfa: int = 1, limit: int = 20) -> List[GitLabProje]:
        """
        Projeleri listele.

        Args:
            arama: Proje adında aranacak metin
            sayfa: Sayfa numarası
            limit: Sayfa başına proje sayısı

        Returns:
            List[GitLabProje]: Proje listesi
        """
        if hasattr(self, '_gl') and self._gl:
            try:
                projeler = []
                gl_projects = self._gl.projects.list(
                    search=arama,
                    page=sayfa,
                    per_page=limit
                )
                for p in gl_projects:
                    proje = GitLabProje(
                        id=p.id,
                        ad=p.name,
                        aciklama=getattr(p, 'description', None),
                        web_url=p.web_url,
                        ssh_url=getattr(p, 'ssh_url_to_repo', None),
                        http_url=getattr(p, 'http_url_to_repo', None),
                        varsayilan_dal=getattr(p, 'default_branch', 'main'),
                        gorunurluk=getattr(p, 'visibility', 'private')
                    )
                    projeler.append(proje)
                    self._projeler[p.id] = proje
                return projeler
            except Exception as e:
                print(f"❌ Proje listesi alınamadı: {e}")
                return []

        # Simülasyon modu
        return self._simulasyon_projeler(arama)

    def _simulasyon_projeler(self, arama: Optional[str] = None) -> List[GitLabProje]:
        """Demo projeler (simülasyon modu için)"""
        demo_projeler = [
            GitLabProje(
                id=1, ad="web-uygulamasi",
                aciklama="Ana web uygulaması",
                web_url=f"{getattr(self, 'url', 'https://gitlab.local')}/web-uygulamasi",
                varsayilan_dal="main"
            ),
            GitLabProje(
                id=2, ad="api-servisi",
                aciklama="REST API servisi",
                web_url=f"{getattr(self, 'url', 'https://gitlab.local')}/api-servisi",
                varsayilan_dal="develop"
            ),
            GitLabProje(
                id=3, ad="mobil-uygulama",
                aciklama="iOS ve Android uygulaması",
                web_url=f"{getattr(self, 'url', 'https://gitlab.local')}/mobil-uygulama",
                varsayilan_dal="main"
            ),
        ]

        if arama:
            return [p for p in demo_projeler if arama.lower() in p.ad.lower()]
        return demo_projeler

    def proje_olustur(self, ad: str, aciklama: Optional[str] = None,
                      gorunurluk: str = "private") -> Optional[GitLabProje]:
        """
        Yeni proje oluştur.

        Args:
            ad: Proje adı
            aciklama: Proje açıklaması
            gorunurluk: Görünürlük (private, internal, public)

        Returns:
            GitLabProje: Oluşturulan proje veya None
        """
        if hasattr(self, '_gl') and self._gl:
            try:
                proje_data = {
                    'name': ad,
                    'description': aciklama,
                    'visibility': gorunurluk
                }
                p = self._gl.projects.create(proje_data)
                proje = GitLabProje(
                    id=p.id,
                    ad=p.name,
                    aciklama=getattr(p, 'description', None),
                    web_url=p.web_url,
                    gorunurluk=gorunurluk
                )
                self._projeler[p.id] = proje
                print(f"✅ Proje oluşturuldu: {proje}")
                return proje
            except Exception as e:
                print(f"❌ Proje oluşturulamadı: {e}")
                return None

        # Simülasyon modu
        yeni_id = max(self._projeler.keys(), default=0) + 1
        proje = GitLabProje(
            id=yeni_id,
            ad=ad,
            aciklama=aciklama,
            web_url=f"{getattr(self, 'url', 'https://gitlab.local')}/{ad}",
            gorunurluk=gorunurluk,
            olusturma_tarihi=datetime.now()
        )
        self._projeler[yeni_id] = proje
        print(f"✅ Proje oluşturuldu (simülasyon): {proje}")
        return proje

    def proje_sil(self, proje_id: int) -> bool:
        """
        Projeyi sil.

        Args:
            proje_id: Silinecek proje ID'si

        Returns:
            bool: Silme başarılı ise True
        """
        if hasattr(self, '_gl') and self._gl:
            try:
                self._gl.projects.delete(proje_id)
                if proje_id in self._projeler:
                    del self._projeler[proje_id]
                print(f"✅ Proje silindi: {proje_id}")
                return True
            except Exception as e:
                print(f"❌ Proje silinemedi: {e}")
                return False

        # Simülasyon modu
        if proje_id in self._projeler:
            del self._projeler[proje_id]
            print(f"✅ Proje silindi (simülasyon): {proje_id}")
            return True
        return False


class GitLabIssueYoneticisi:
    """
    GitLab issue (sorun) yönetimi için sınıf.
    """

    def __init__(self):
        self._issues: Dict[int, GitLabIssue] = {}

    def issuelari_listele(self, proje_id: int, durum: str = "opened",
                          limit: int = 20) -> List[GitLabIssue]:
        """
        Proje issue'larını listele.

        Args:
            proje_id: Proje ID'si
            durum: Issue durumu (opened, closed, all)
            limit: Maksimum sonuç sayısı

        Returns:
            List[GitLabIssue]: Issue listesi
        """
        if hasattr(self, '_gl') and self._gl:
            try:
                project = self._gl.projects.get(proje_id)
                issues = project.issues.list(state=durum, per_page=limit)
                return [
                    GitLabIssue(
                        id=i.id,
                        iid=i.iid,
                        baslik=i.title,
                        aciklama=getattr(i, 'description', None),
                        durum=i.state,
                        proje_id=proje_id,
                        etiketler=getattr(i, 'labels', [])
                    )
                    for i in issues
                ]
            except Exception as e:
                print(f"❌ Issue listesi alınamadı: {e}")
                return []

        # Simülasyon modu
        return self._simulasyon_issues(proje_id)

    def _simulasyon_issues(self, proje_id: int) -> List[GitLabIssue]:
        """Demo issue'lar"""
        return [
            GitLabIssue(
                id=101, iid=1, baslik="Login sayfası düzeltmesi",
                aciklama="Login butonuna tıklanınca hata veriyor",
                durum="opened", proje_id=proje_id,
                etiketler=["bug", "priority::high"]
            ),
            GitLabIssue(
                id=102, iid=2, baslik="Yeni dashboard özelliği",
                aciklama="Kullanıcı dashboard'u eklenmeli",
                durum="opened", proje_id=proje_id,
                etiketler=["feature", "priority::medium"]
            ),
        ]

    def issue_olustur(self, proje_id: int, baslik: str,
                      aciklama: Optional[str] = None,
                      etiketler: Optional[List[str]] = None) -> Optional[GitLabIssue]:
        """
        Yeni issue oluştur.

        Args:
            proje_id: Proje ID'si
            baslik: Issue başlığı
            aciklama: Issue açıklaması
            etiketler: Etiket listesi

        Returns:
            GitLabIssue: Oluşturulan issue veya None
        """
        if hasattr(self, '_gl') and self._gl:
            try:
                project = self._gl.projects.get(proje_id)
                issue_data = {
                    'title': baslik,
                    'description': aciklama,
                    'labels': etiketler or []
                }
                i = project.issues.create(issue_data)
                issue = GitLabIssue(
                    id=i.id,
                    iid=i.iid,
                    baslik=i.title,
                    aciklama=getattr(i, 'description', None),
                    durum=i.state,
                    proje_id=proje_id,
                    etiketler=etiketler or []
                )
                print(f"✅ Issue oluşturuldu: {issue}")
                return issue
            except Exception as e:
                print(f"❌ Issue oluşturulamadı: {e}")
                return None

        # Simülasyon modu
        yeni_iid = len(self._issues) + 1
        issue = GitLabIssue(
            id=200 + yeni_iid,
            iid=yeni_iid,
            baslik=baslik,
            aciklama=aciklama,
            durum="opened",
            proje_id=proje_id,
            etiketler=etiketler or [],
            olusturma_tarihi=datetime.now()
        )
        self._issues[issue.id] = issue
        print(f"✅ Issue oluşturuldu (simülasyon): {issue}")
        return issue

    def issue_kapat(self, proje_id: int, issue_iid: int) -> bool:
        """Issue'u kapat."""
        if hasattr(self, '_gl') and self._gl:
            try:
                project = self._gl.projects.get(proje_id)
                issue = project.issues.get(issue_iid)
                issue.state_event = 'close'
                issue.save()
                print(f"✅ Issue kapatıldı: #{issue_iid}")
                return True
            except Exception as e:
                print(f"❌ Issue kapatılamadı: {e}")
                return False

        print(f"✅ Issue kapatıldı (simülasyon): #{issue_iid}")
        return True


class GitLabOnPrem(GitLabBaglantisi, GitLabProjeYoneticisi, GitLabIssueYoneticisi):
    """
    GitLab On-Premise tam entegrasyon sınıfı.

    Bu sınıf, çoklu kalıtım kullanarak tüm GitLab işlemlerini
    tek bir sınıfta birleştirir.

    Örnek Kullanım:
        # Bağlantı oluştur
        gitlab = GitLabOnPrem(
            url="https://gitlab.sirketiniz.com",
            private_token="glpat-xxxxxxxxxxxx"
        )

        # Bağlan
        if gitlab.baglan():
            print(f"Hoşgeldin, {gitlab.kullanici}!")

            # Projeleri listele
            projeler = gitlab.projeleri_listele()
            for proje in projeler:
                print(f"  - {proje}")

            # Yeni proje oluştur
            yeni_proje = gitlab.proje_olustur(
                ad="yeni-proje",
                aciklama="Test projesi"
            )

            # Issue oluştur
            if yeni_proje:
                gitlab.issue_olustur(
                    proje_id=yeni_proje.id,
                    baslik="İlk görev",
                    aciklama="Projeyi kur",
                    etiketler=["setup"]
                )
    """

    def __init__(self, url: str, private_token: Optional[str] = None,
                 oauth_token: Optional[str] = None):
        """
        GitLab On-Premise bağlantısı oluştur.

        Args:
            url: GitLab sunucu URL'si (örn: https://gitlab.sirketiniz.com)
            private_token: Kişisel erişim token'ı (Settings > Access Tokens)
            oauth_token: OAuth2 token (opsiyonel, SSO için)

        Not:
            Token oluşturmak için:
            1. GitLab'a giriş yapın
            2. Settings > Access Tokens
            3. Gerekli izinleri seçin (api, read_api, read_repository, write_repository)
            4. Token'ı güvenli bir yerde saklayın
        """
        # Çoklu kalıtımda super() kullanımı
        GitLabBaglantisi.__init__(self, url, private_token, oauth_token)
        GitLabProjeYoneticisi.__init__(self)
        GitLabIssueYoneticisi.__init__(self)

        self._simulasyon_modu = False

    def durum_ozeti(self) -> str:
        """Bağlantı ve kullanım özeti döndür."""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║              GitLab On-Premise Entegrasyonu                 ║
╠══════════════════════════════════════════════════════════════╣
║  Sunucu  : {self.url:<48} ║
║  Durum   : {self.durum.value:<48} ║
║  Kullanıcı: {str(self.kullanici) if self.kullanici else 'Bağlı değil':<47} ║
║  Mod     : {'Simülasyon' if self._simulasyon_modu else 'Gerçek':<48} ║
╚══════════════════════════════════════════════════════════════╝
"""

    def hizli_baslangic(self):
        """Hızlı başlangıç demo fonksiyonu."""
        print("\n🚀 GitLab On-Premise Hızlı Başlangıç")
        print("=" * 50)

        # Bağlan
        print("\n1️⃣  Sunucuya bağlanılıyor...")
        if not self.baglan():
            print("❌ Bağlantı başarısız!")
            return

        print(self.durum_ozeti())

        # Projeleri listele
        print("\n2️⃣  Projeler listeleniyor...")
        projeler = self.projeleri_listele()
        if projeler:
            print(f"   {len(projeler)} proje bulundu:")
            for p in projeler[:5]:
                print(f"   📁 {p}")

        # Demo proje oluştur
        print("\n3️⃣  Demo proje oluşturuluyor...")
        demo_proje = self.proje_olustur(
            ad="gitlab-onprem-test",
            aciklama="GitLab On-Premise entegrasyon testi"
        )

        if demo_proje:
            # Issue oluştur
            print("\n4️⃣  Demo issue oluşturuluyor...")
            self.issue_olustur(
                proje_id=demo_proje.id,
                baslik="Entegrasyon testi",
                aciklama="GitLab On-Prem entegrasyonu başarıyla çalışıyor!",
                etiketler=["test", "demo"]
            )

            # Issue'ları listele
            print("\n5️⃣  Issue'lar listeleniyor...")
            issues = self.issuelari_listele(demo_proje.id)
            for issue in issues:
                print(f"   📋 {issue}")

        print("\n✅ Hızlı başlangıç tamamlandı!")
        print("=" * 50)


def demo():
    """
    GitLab On-Premise entegrasyonu demo fonksiyonu.

    Bu fonksiyon, GitLab On-Prem entegrasyonunun
    temel özelliklerini gösterir.
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🦊 GitLab On-Premise Entegrasyonu Demo              ║
║                                                              ║
║  Bu demo, kendi sunucunuzda barındırılan GitLab ile         ║
║  nasıl entegre olunacağını gösterir.                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    # Ortam değişkenlerinden veya varsayılan değerlerle bağlantı
    gitlab_url = os.environ.get("GITLAB_URL", "https://gitlab.sirketiniz.com")
    gitlab_token = os.environ.get("GITLAB_TOKEN", None)

    print(f"📡 Hedef GitLab Sunucusu: {gitlab_url}")
    print()

    # GitLab On-Prem instance oluştur
    gitlab = GitLabOnPrem(
        url=gitlab_url,
        private_token=gitlab_token
    )

    # Hızlı başlangıç demo'sunu çalıştır
    gitlab.hizli_baslangic()

    # Ek bilgiler
    print("""
╔══════════════════════════════════════════════════════════════╗
║                     Kullanım Bilgileri                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🔧 Gerçek GitLab sunucusuna bağlanmak için:                ║
║                                                              ║
║     1. python-gitlab kütüphanesini kurun:                   ║
║        pip install python-gitlab                             ║
║                                                              ║
║     2. Ortam değişkenlerini ayarlayın:                      ║
║        export GITLAB_URL="https://gitlab.sirketiniz.com"    ║
║        export GITLAB_TOKEN="glpat-xxxxxxxxxxxx"             ║
║                                                              ║
║     3. Veya doğrudan parametrelerle:                        ║
║        gitlab = GitLabOnPrem(                                ║
║            url="https://gitlab.sirketiniz.com",             ║
║            private_token="glpat-xxxxxxxxxxxx"               ║
║        )                                                     ║
║                                                              ║
║  📚 Dokümantasyon:                                          ║
║     https://python-gitlab.readthedocs.io                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    demo()
