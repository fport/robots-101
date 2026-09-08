# Ne kadarını, ne zaman bilmeliyim?

İlk komutları çalıştırmak başlangıç için yeterli. Kendi görevini kurmak, eğitmek ve başarısızlığı açıklamak için **mekanik → ölçüm → kontrol → veri → öğrenme → değerlendirme** zincirini anlayabilmen gerekir. Bu rehberde “hero”, her robotik makaleyi ezberlemek değil; bu zincirde bir sorun olduğunda hangi ölçümle başlayacağını bilmektir.

Her şeyi ilk hafta öğrenmeye çalışma. Aşağıdaki sıralama, robot gelmeden yapabileceklerinle donanım gerektiren işleri ayırır. Süreler zorunlu takvim değildir; bir aşamayı bitiren şey ürettiğin kanıttır.

## 1. Robot gelmeden: bilgisayarında deney kurabilmek

Python ortamını seçebilmek, terminalde doğru klasörde olmak, bir traceback'in son satırını okumak, dosya yollarını ve birimleri ayırt etmek gerekiyor. Python uzmanlığı gerekmiyor. Fakat `python` ile `.venv/bin/python` farklı paketleri kullanıyorsa nedenini bulabilmelisin.

Bir robot komutunu şu altı soruyla okuyabil:

1. Hangi robota, hangi ekleme gönderiliyor?
2. Değer hedef konum mu, hız (velocity) mı, tork (torque) mu?
3. Birim radyan mı, derece mi, normalize değer mi?
4. Fizik veya donanım ne kadar zaman ilerliyor?
5. Komuttan sonra gerçekte hangi değer ölçülüyor?
6. Başarılı saymak için hangi koşul, kaç ölçüm boyunca sağlanmalı?

**Bitirme kanıtı:** [hedef takibi deneyini](../simulasyon/denetleyici.md) çalıştırıp CSV'den bir satırı açıklamak. `command`, `q_before`, `q_after` ve `goal` aynı şeymiş gibi anlatıyorsan bu aşamaya geri dön.

## 2. Görevi tasarlarken: geometri ve gözlem

“Kırmızı küpü al” cümlesi henüz kontrol problemi tanımı değildir. Küpün nerede başlayacağı, kameranın neyi göreceği, kolun hangi yönden yaklaşacağı, tutucunun ne zaman kapanacağı ve bırakmanın nasıl ölçüleceği belirsizdir.

[Kinematik ve IK](../temel/kinematik-ik.md) bölümündeki iki eklemli hesabı yap. Sonra SO-101'in beş kol eklemiyle neden her konum-yönelim isteğini bağımsız sağlayamadığını anlat. [Kamera geometrisinde](../donanim/kamera-kalibrasyonu.md) bir pikselin neden tek başına üç boyutlu konum olmadığını öğren.

**Bitirme kanıtı:** görevin bir sayfalık tanımı: başlangıç bölgesi, nesneler, gözlem (observation) kaynakları, eylem (action) birimi, bitiş koşulu, zaman aşımı (timeout). [Bitirme projesi](../pratik/proje.md) bunun şablonudur.

## 3. Robot gelince: tekrar edilebilir gösterim

Bu aşamada motor ID, servo kalibrasyonu, kamera kalibrasyonu ve model normalizasyonunun ayrı işler olduğunu bilmelisin. Birini yapmak diğerlerini tamamlamaz. Leader ile yaptığın hareketin follower üzerinde beklenen yönü ve aralığı üretmesi gerekir.

Önce beş pilot bölüm (episode) topla. Her birinin videosunu izle; action/durum (state) izini incele. Nesne görünmezken tutucu (gripper) kapanıyorsa veya görüntü hareketten sonra geliyorsa bunu model büyüterek çözmeye çalışma. [Veri mühendisliği](../ogrenme/veri-muhendisligi.md) bu kontrolleri açıklar.

**Bitirme kanıtı:** başka bir gün aynı kamera/kalibrasyon (calibration) düzenini yeniden kurabildiğin cihaz ve kayıt notu; sorunlu episode'ları nedenleriyle ayırdığın küçük bir inceleme tablosu.

## 4. İlk eğitim: neyin optimize edildiğini anlamak

Tensor, örnek grubu (batch), normalization, eylem dizisi (action chunk), doldurma (padding) mask, loss, eniyileyici (optimizer), kontrol noktası (checkpoint) ve doğrulama (validation) kavramlarını kullanabilmelisin. Türevlerin tüm ispatlarını bilmek zorunda değilsin; loss'un hangi örnekler üzerinde, hangi ölçekte hesaplandığını bilmek zorundasın.

[SmolVLA'nın iç yapısı](../ogrenme/smolvla-ic-yapi.md) bölümündeki iki sayılık flow matching hesabını elle yap. Sonra [eğitim deneyleri](../ogrenme/egitim-deneyleri.md) bölümünden bir hipotez seç: örneğin “bilek kamerası kapanış anını görmeyi iyileştiriyor mu?” Tek koşuda kamera, öğrenme oranı (learning rate) ve veri miktarını beraber değiştirme.

**Bitirme kanıtı:** aynı görev koşullarıyla karşılaştırılmış iki deney; kullanılan veri sürümü, checkpoint, loss ve politika yürütümü (rollout) sonuçları kayıtlı. Eğitim (training) tamamlanması ile görev başarısını ayrı raporluyorsun.

## 5. İleri seviye: sınırlarını ölçmek

Artık temas (contact) fiziği, sistem tanılama, domain randomization, daha ayrıntılı IK, görev planlama, asenkron çıkarım (inference) ve gerektiğinde RL anlamlı olur. Bunların hepsini ilk çalışan pick-and-place öncesinde bitirmen gerekmez. ROS 2 de bu atölyedeki temel sim/LeRobot hattının ön koşulu değildir; başka sensör ve düğümlerle entegrasyon gerektiğinde öğrenilir.

**Bitirme kanıtı:** modelin eğitim dağılımı dışında nerede bozulduğunu gösteren testler. Örneğin nesneyi yeni bir başlangıç bölgesine koyunca başarı düşüyor, aynı bölgeye yönelik ek gösterimle sonuç değişiyor. “Bazen çalışıyor” yerine hata türü, koşul ve sayım verebiliyorsun.

## Derin okuma sırası

| Sıra | Bölüm | Cevaplayacağın soru |
|---|---|---|
| 1 | [Kinematik ve IK](../temel/kinematik-ik.md) | Uç hedefinden eklem (joint) açısına nasıl geçilir? |
| 2 | [Ölçülen durumla denetleyici](../simulasyon/denetleyici.md) | Hareketin tamamlandığını nasıl anlarım? |
| 3 | [Kamera geometrisi](../donanim/kamera-kalibrasyonu.md) | Kamera ile robot aynı noktayı nasıl tarif eder? |
| 4 | [Veri mühendisliği](../ogrenme/veri-muhendisligi.md) | Bir eğitim örneği hangi zamanları içerir? |
| 5 | [SmolVLA'nın iç yapısı](../ogrenme/smolvla-ic-yapi.md) | Modelin loss'u gerçekte neyi öğretir? |
| 6 | [Eğitim deneyleri](../ogrenme/egitim-deneyleri.md) | Düşük loss'a rağmen kötü davranışı nasıl incelerim? |
| 7 | [Çözümlü sınama](../pratik/cozumlu-sorular.md) | Bunları yardım almadan açıklayabiliyor muyum? |

## Bu rehberin kapsam sınırı

Yerelde çalışan örnekler arasında gerçek SO-101 modelinde eklem hedefi takibi, görüntülü kayıt, veri okuma ve küçük bir BC eğitimi var. Henüz doğrulanmış uçtan uca **SmolVLA ile nesne kavrama** sonucu yok. Gerçek kol ve GPU üzerinde yeni deneyler yapıldıkça [doğrulama kaydına](dogrulama.md) eklenmesi gerekir. Bir kitap kadar açıklama bu deneylerin yerini tutmaz; onları daha bilinçli yapmanı sağlar.
