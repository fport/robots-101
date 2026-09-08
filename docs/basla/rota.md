# Öğrenme rotası

Robotikle ilk kez tanışıyorsan önce [tamamen sıfırdan girişini](sifirdan.md) oku. Robot gelmeden [sıfırdan MuJoCo dünyasını](../simulasyon/sifirdan.md), [on fizik deneyini](../simulasyon/deneyler.md) ve [ilk öğrenme döngüsünü](../ogrenme/ilk-ogrenme.md) tamamlayabilirsin. Hazır veriyi [Hugging Face bölümünde](../ogrenme/huggingface.md) indirip okuyacaksın; kendi sayısal verini [üretim bölümünde](../ogrenme/veri-uretimi.md) oluşturacaksın. Yeni çalışmalar laboratuvar defterinde 17–22 numaralarıyla bulunur.

İlk on iki uygulama çalışma hattını kurar. Kavramları daha derinden anlamak için [bilgi seviyeleri ve derin okuma rotasını](derinlik.md) izle; yeni IK, denetleyici (controller), eylem (action) window ve flow matching uygulamaları [laboratuvar defterinin 13–16. deneylerinde](../pratik/lablar.md#lab-13-iki-ik-dal) bulunur. Aşağıdaki 12 kutu başlangıç rotasının ilerlemesidir; bütün uzmanlık konularının puanı değildir.

Hedef her komutu ezberlemek değil; bir hata çıktığında bunun fizik, haberleşme, veri veya model katmanından geldiğini ayırt edebilmek. Aşağıdaki süreler çalışma önerisidir; donanım teslim tarihi veya eğitim (training) süresi tahmini değildir.

## Dört aşamada ilerle

| Aşama | Çalışma | Tamamlanma kanıtı |
|---|---|---|
| 1 · Robot gelmeden, ilk birkaç oturum | Kurulum, birimler, MuJoCo, SO-101 sahnesi | Kendi ürettiğin PNG, durum (state) çıktısı ve hedef takip CSV'si |
| 2 · Veri hattı | bölüm (Episode), action/state farkı, sim kaydı, denetim | Gerçekte 3 episode içeren ve denetimden geçen veri seti (dataset) |
| 3 · Donanım geldiğinde | Sabitleme, port, kalibrasyon (calibration), teleop, kamera | Kontrollü ilk hareket ve 5 pilot gösterim (demonstration) |
| 4 · Öğrenme döngüsü | Veri iyileştirme, ACT, SmolVLA, değerlendirme | Ayrılmış test görevlerinde ölçülmüş başarı oranı (success rate) |

Her aşamada küçük bir deney notu tut: tarihi, paket sürümlerini, değiştirdiğin tek şeyi, gözlenen sonucu ve sonraki soruyu yaz. Bir videonun dosya adı bile deney numarasını içerirse sonradan karşılaştırma kolaylaşır: `run-004_camera-front_ep-003.mp4`.

## İlerleme defterin

Bu kutular yalnız bu tarayıcıda saklanır. Sunucu hesabı veya bulut senkronizasyonu yoktur. Tarayıcı verisini temizlersen işaretler silinir.

<div class="progress-list lab-panel" id="learning-progress">
<p id="progress-summary" aria-live="polite"></p>
<progress max="12" value="0" aria-label="Öğrenme ilerlemesi"></progress>
<label><input type="checkbox" id="p01">01 — Python ortamlarını ayırdım ve doctor çıktısını okudum.</label>
<label><input type="checkbox" id="p02">02 — Derece/radyan, eklem (joint)/uç nokta farkını açıklayabiliyorum.</label>
<label><input type="checkbox" id="p03">03 — MuJoCo tek eklem deneyini çalıştırdım.</label>
<label><input type="checkbox" id="p04">04 — Strands ile SO-101 görüntüsünü kendim ürettim.</label>
<label><input type="checkbox" id="p05">05 — Üç sim episode kaydettim ve sayıları denetledim.</label>
<label><input type="checkbox" id="p06">06 — Donanımı sabitledim; kit güç ve kalibrasyon bilgilerini doğruladım.</label>
<label><input type="checkbox" id="p07">07 — Leader ile kontrollü teleop yaptım, iki kamerayı doğruladım.</label>
<label><input type="checkbox" id="p08">08 — Beş pilot gösterimi tek tek izledim ve sorunları düzelttim.</label>
<label><input type="checkbox" id="p09">09 — Veri toplama planımı tamamladım; test koşullarını ayırdım.</label>
<label><input type="checkbox" id="p10">10 — ACT veya SmolVLA kısa eğitim denemesini bitirdim.</label>
<label><input type="checkbox" id="p11">11 — Ayrı değerlendirme denemelerinde sonuç ve hata nedeni tuttum.</label>
<label><input type="checkbox" id="p12">12 — Bir veri iyileştirmesini yeni kontrol noktası (checkpoint) ile karşılaştırdım.</label>
<button type="button">İşaretleri sıfırla</button>
</div>

Türkçe ve İngilizce arasında geçince aynı ilerleme kullanılır. Site dilini değiştirmek kayıtlı modelin görev dilini veya öğrendiklerini değiştirmez.

## Leader ve GPU kararları

**Leader + follower varsa:** gerçek gösterim toplamada en doğrudan rota leader teleoperasyonudur. Leader'ın hareketini ölçüp follower için hedefe dönüştürürsün. Başta model gerekmez.

**Yalnız follower varsa:** bütün sim ve hazır veri alıştırmaları yapılabilir. Gerçek gösterim için uyumlu bir kontrolcü, klavye/gamepad + kinematik eşleme ya da sonradan leader gerekir. Klavyedeki `x += 1` komutu motor hedefi değildir; IK, limitler ve hız (velocity) yönetimi eklenmelidir. Kolu motor torku açıkken elle zorlayarak gösterim toplamaya çalışma.

**Yalnız Mac varsa:** CPU simülasyonu ve veri inceleme ile başla. Apple Silicon'da MPS bazı eğitim/çıkarım (inference) işlerinde kullanılabilir; paket, işlem ve bellek uyumluluğunu küçük koşuyla sınarsın. NVIDIA CUDA eğitim tarifini ayrı makinede uygulamak da mümkündür. İlk hedef GPU satın almak değil, sorunsuz bir küçük veri hattı oluşturmaktır.

## “Hero” için bitirme ölçütü

Tek başarılı videoyu paylaşmak yerine belirlenmiş 20 testin tamamını, kullanılan checkpoint'i ve hata dağılımını raporla. Örneğin “aynı ışık, beş başlangıç bölgesi, dört tekrar; 14/20 başarı” ifadesi test edilmeyen bütün nesnelerde çalıştığı iddiasından çok daha anlamlıdır. Bu sayılar bir atölye değerlendirme tasarımıdır; evrensel başarı eşiği değildir.
