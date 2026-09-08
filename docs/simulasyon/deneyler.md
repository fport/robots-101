# MuJoCo ile 10 kullanım deneyi

Her deneyde önce tahmin yaz, sonra çalıştır, çıktıdan bir sayı çıkar. `examples/13_mujoco_playground.py` beş sahne davranışı sunar; seçenekleri değiştirerek aşağıdaki on soruyu sınayabilirsin. Model, küp ve tek eklemli öğretim koludur; SO-101 modeli değildir.

## 1. Düşen nesne ve temas

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene drop --output outputs/e01
```

Başlangıç yüksekliği 0.60 m, son merkez yüksekliği yaklaşık 0.02497 m. Temas (contact) sayısı sıfırdan artar. Yerleşme yüksekliğinin küpün yarı boyutuna yakın olması beklenir. Küçük penetrasyon farkı, yumuşak temas çözümüyle ilişkili olabilir; metre yerine milimetre ölçeğini de incele.

## 2. Yerçekimini kapat

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene drop --gravity 0 --output outputs/e02
```

Küpün yüksekliği 0.60 m'de kalır; temas oluşmaz. Birinci deneyle yalnız yerçekimi (gravity) değişti. “Sim çalışmıyor” ile “modelde hareketi üreten etki yok” farklı durumlardır.

## 3. Az sürtünmeyle kayma

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene slide --friction 0.1 --output outputs/e03
```

Küp zemine yakın başlar; başlangıç x hızı 0.8 m/s'dir. Yerel ölçümde yaklaşık 0.3256 m ilerledi. Kayma sürtünmesi (sliding friction) enerjinin azalmasını etkiler. Burada hem küp hem zemindeki kayma sürtünmesi aynı değere ayarlanır; yalnız birini değiştirmek temas birleştirme kuralları nedeniyle farklı sonuç verebilir.

## 4. Yüksek sürtünmeyle karşılaştır

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene slide --friction 1 --output outputs/e04
```

Yerel ölçüm yaklaşık 0.02976 m. İki koşunun `cube_x_displacement_m` değerini karşılaştır. Bu sayılar belirli model ve başlangıç içindir; gerçek masanın sürtünmesini ölçmüş olmazsın. Farkı anlamak için aynı başlangıç, süre ve kütleyi koru.

## 5. Motor hedefi takip etsin

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene servo --target 0.7 --output outputs/e05
```

Hedef konum aktüatörü (position actuator) açıyı takip eder. 3 sim saniyesi sonunda bu modelde açı yaklaşık 0.7 rad olur. `command_rad` hedef, `pan_rad` ölçülen konumdur. Kolun ekseni dikey olduğundan bu deney yerçekimine karşı omuz kaldırma deneyi değildir.

## 6. Kazanç ve sönüm

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene servo --kp 10 --damping 0.2 --output outputs/e06
```

Oransal kazanç (proportional gain, kp) ve sönüm (damping) takip geçişini etkiler. Bu komutta ikisi değiştiği için tek bir neden atayamazsın; bir sonraki karşılaştırmada birini sabitle. CSV'de bütün açı eğrisini incele; son değer aynı olsa da salınım farklı olabilir.

MuJoCo position aktüatörünün katsayısını runtime'da değiştirirken script hem gain hem bias içindeki kp terimini değiştirir. Yalnız gain'i değiştirmek XML'de kp'yi değiştirmekle aynı matematiği korumaz. [Aktüatör modellemesi](https://mujoco.readthedocs.io/en/stable/modeling.html#actuator-shortcuts)

## 7. Kısa dış kuvvet uygula

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene push --output outputs/e07
```

İlk 0.20 s boyunca x yönünde 0.4 N dış kuvvet (external force), sonra sıfır uygulanır. Script `xfrc_applied` alanını her adım temizler; aksi halde önceki kuvveti sürdürmek kolaydır. Yerel koşuda küp yaklaşık 0.05828 m ilerledi. Bu, gerçek tutucunun nesneyi itmesi yerine doğrudan gövdeye uygulanan kuvvettir.

## 8. Kontrollü rastgele başlangıç

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene random --seed 7 --output outputs/e08a
.venv/bin/python examples/13_mujoco_playground.py --scene random --seed 7 --output outputs/e08b
.venv/bin/python examples/13_mujoco_playground.py --scene random --seed 8 --output outputs/e08c
```

Rastlantı başlangıç değeri (seed), örnekleme sırasını belirler. Aynı ortam/sürümde ilk iki koşunun başlangıç konumları eşleşmeli; üçüncüsü değişmeli. Script küp konumu ve rengini çeşitlendirir; tüm fizik parametrelerini rastgeleleştirmez. Alan çeşitlendirmesi (domain randomization) yaparken hangi değişkenin hangi dağılımdan geldiğini kaydet.

## 9. RGB ve derinlik görüntüsü

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene servo --render --output outputs/e09
```

`rgb.png`, 640×480 renk görüntüsü; `depth_m.npy`, piksel başına metre cinsinden derinlik dizisidir. Model dosyasındaki `camera` konumunu kopya bir sahnede değiştirerek nesnenin görünürlüğünü karşılaştır. Sim kamerasından alınan ideal derinlik, gerçek RGB kameranın doğrudan ürettiği veri değildir.

Bu Mac'te görüntüler üretildi; grafik sürücüsü derinlik doğruluğunun sınırlı olabileceğini bildirdi (`ARB_clip_control`). Bu yüzden derinlik dosyasının oluşmasını hassas mesafe doğrulaması olarak sunmuyoruz. [MuJoCo rendering API](https://mujoco.readthedocs.io/en/stable/python.html)

## 10. Başlangıca dön ve yeni deney kur

Her koşunun sonunda script `mj_resetData` çağırıp sakladığı başlangıç konum/hızlarını geri koyar ve `mj_forward` çalıştırır. Raporda `reset_time_s=0`, `reset_qpos_max_error=0` beklenir. Modelde sonradan değiştirdiğin renk/sürtünme (friction) gibi parametreler durum reset'iyle otomatik geri alınmaz; model (model) ve durum (state) farkını burada tekrar görürsün.

**Deney:** yeni bir seed ile başlamayı aynı başlangıcı reset etmekten ayır. İlki yeni bölüm başlangıcı örnekler, ikincisi kayıtlı başlangıca döner. Eğitimde ikisine de ihtiyaç olabilir.

## Bu deneyleri SO-101'e bağla

Tek eklem (joint) ve küp deneylerini anlayınca [gerçek SO-101 modeliyle hedef takibini](denetleyici.md) yap. Orada “bir motor” yerine altı eylem (action) anahtarı, her hedef için hata koşulu ve aşama geçişleri var. Sonra [kayıt](veri.md) ve [veriden öğrenme](../ogrenme/ilk-ogrenme.md) hattına geç.

**Tamamlama ölçütü:** en az üç farklı koşudan CSV/JSON sakladın, sonucu bir sayı ile karşılaştırdın ve değişikliğin neden etkili olduğunu açıklayabiliyorsun. Pencerenin açılması tek başına bu deneylerin bitirme koşulu değildir.
