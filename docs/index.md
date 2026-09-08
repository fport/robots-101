---
hide:
  - toc
---

<div class="hero" markdown>
<div class="eyebrow">SO-101 ATÖLYESİ / ZERO TO HERO</div>

# Robotun gelmeden.<br>İlk hareketinden önce.

<p class="intro">Masaüstündeki bir robot kolu anlamaktan, kendi gösterimlerinle eğittiğin bir modele kadar. Türkçe açıklamalar, gerçek MuJoCo deneyleri ve adım adım bir çalışma defteri.</p>

<div class="hero-actions" markdown>
[İlk 30 dakikaya başla](basla/kurulum.md){ .md-button .md-button--primary }
[Tarayıcıda dene](temel/laboratuvar.md){ .md-button }
</div>

<p class="quiet">Referans: 8 Eylül 2026 · Python 3.12 · Strands Robots 0.5.1 · LeRobot 0.6.1</p>
</div>

<div class="route-grid" markdown>
<div class="route-card" markdown>
<span class="number">01 / ANLA</span>

### Kolun dilini öğren

Eklemler, koordinatlar, motor hedefleri, kameralar. Bir komutun fiziksel harekete nasıl dönüştüğünü izle.

[Robotik temeli →](temel/robotik.md)
</div>
<div class="route-card" markdown>
<span class="number">02 / DENE</span>

### Simülasyonda çalış

MuJoCo sahnesini aç, SO-101'i yükle, durumu oku, hareketi ve kamerayı kaydet. İlk aşamada robot ve LLM hesabı gerekmiyor.

[MuJoCo atölyesi →](simulasyon/mujoco.md)
</div>
<div class="route-card" markdown>
<span class="number">03 / ÖĞRET</span>

### Veriden davranışa

Gösterim kalitesini ölç, LeRobot veri setini denetle, SmolVLA fine-tuning komutunu hazırla ve başarıyı sınayan deney kur.

[SmolVLA eğitimi →](ogrenme/smolvla.md)
</div>
</div>

## Bu atölyenin sonunda ne yapacaksın?

!!! tip "Komutları çalıştırdım; daha derine inmek istiyorum"
    [Ne kadarını, ne zaman bilmeliyim?](basla/derinlik.md) sayfası bilgi seviyelerini somut bitirme koşullarına bağlar. Kinematik/IK, ölçülen durumla SO-101 kontrolü, kamera geometrisi, veri zamanlaması ve SmolVLA'nın öğrenme hesabı için derin okuma rotasını izle. [16 çözümlü soruyla](pratik/cozumlu-sorular.md) kendini sına.

İlk proje: **bir nesneyi alıp belirli bir kaba bırakmak**. Bunun öncesinde eklem hedefi takibi, kamera yerleşimi ve veri kaydı gibi daha küçük işleri bitireceksin. Başarı ölçütünü baştan belirleyecek, eğitim verisiyle test verisini ayıracak, başarısız denemeleri nedenlerine göre inceleyeceksin.

Rehber iki paralel rotaya sahip. Robot henüz yokken MuJoCo ve Strands ile çalışırsın. Donanım geldiğinde aynı kavramları leader/follower teleoperasyonu ve kamera kaydına taşırsın. Model eğitimi için ayrı bir Python ortamı kullanılır; Mac üzerinde simülasyon yaparken eğitim başka bir NVIDIA GPU bilgisayarda yürüyebilir.

!!! tip "İsimleri yerli yerine koyalım"
    Aklındaki simülatör **MuJoCo**. **Strands Robots** robot araçlarını bir araya getirir. **LeRobot** robot sürücüleri, veri setleri ve öğrenme altyapısını sağlar. **SmolVLA** görüntü, görev metni ve robot durumundan eylem tahmin eden bir politikadır. [Yazılım haritası](temel/yigin.md) bağlantıları açar.

## Burada ne gerçekten çalışıyor?

| Parça | Ne yapar? | Gereken |
|---|---|---|
| İnteraktif mini laboratuvar | Kinematik, veri miktarı, eylem ufku hesabı | Tarayıcı |
| `01_mujoco_basics.py` | Fizik motorunda tek eklem hedef takibi | Sim ortamı |
| `02_strands_so101.py` | SO-101 modelini yükler, mock hareket ve PNG üretir | İlk model indirmesinde internet |
| `03_record_sim.py` | Ayrı episode'ları LeRobot biçiminde kaydeder | ML ortamı ve video bağımlılıkları |
| `09_so101_waypoints.py` | Gerçek SO-101 sim modelinde üç hedefi ölçerek tamamlar | Sim ortamı |
| `10_action_windows.py` | Episode sınırı, action chunk ve padding hesabı | Küçük LeRobot dataset, ML ortamı |
| `11_flow_matching.py` / `12_planar_ik.py` | Öğrenme hesabı ve iki dallı kinematik çözüm | Sim ortamındaki NumPy |
| Veri denetimi ve eğitim hazırlığı | Şema/zaman kontrolleri ve çalıştırılacak komut | Veri seti |
| Gerçek kol ve SmolVLA rollout | Donanım üzerinde öğrenilmiş davranış | Kalibrasyon, veri, checkpoint ve uygun bilgisayar |

Mock bir politikanın sorunsuz çalışması, nesne kavramayı öğrendiği anlamına gelmez. Tarayıcıdaki kol çizimi de MuJoCo değildir; iki eklemli matematik alıştırmasıdır. Her bölüm, deneyin neyi gösterdiğini açıklar. [Çalıştırma sonuçlarını ve henüz sınanmayan adımları oku.](basla/dogrulama.md)

## Okuma biçimi

Sırayla ilerlemek için [öğrenme rotasını](basla/rota.md) aç. Her laboratuvarda amaç, komut, beklenen çıktı, değiştireceğin değişken ve bitirme koşulu bulunur. Bir hata çıkarsa [sorun giderme tablosu](pratik/sorunlar.md) ile ilgili katmana dön. Bütün teknik kaynaklar ilgili sayfada ve [kaynak defterinde](kaynaklar.md) bağlantılıdır.

Bu, Hashtag Robotics'in resmî kılavuzu değildir. Senin verdiğin ürün sayfası donanım bağlamı olarak kullanıldı. Kitin gerçek parça listesi, güç etiketleri ve satıcının kalibrasyon talimatları teslim edilen cihaz için esas alınmalıdır.
