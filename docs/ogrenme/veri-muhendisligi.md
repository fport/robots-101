# Veri mühendisliği: zaman, etiket ve bölme

Bir Parquet dosyasının açılması eğitim verisinin doğru olduğu anlamına gelmez. Hangi görüntünün hangi eyleme eşlendiği, episode'un nerede bittiği ve test örneklerinin eğitimden gerçekten ayrı olup olmadığı modelin öğrendiği problemi belirler.

Bu bölümde mevcut 3 episode/90 karelik smoke kaydını kullanarak action chunk çıkaracağız. Veri hattını öğrenmek için uygun; görev uzmanlığı içermediği için bu kayıttan kavrama başarısı beklenmez.

## 1. Bir örneğin zaman sözleşmesi

Bir karar adımını şu şekilde tanımla:

```text
o_t = karardan önce mevcut gözlem (kamera + ölçülen eklem durumu)
a_t = bu gözleme dayanarak gönderilen eylem
o_(t+1) = eylem uygulanıp zaman ilerledikten sonraki gözlem
```

BC örneği `o_t → a_t` eşleşmesini öğrenir. `o_(t+1) → a_t` yazarsan modele karar anında henüz bulunmayan bilgi verebilirsin. Gözlemden önceki eylemi yazarsan da başka bir gecikme ilişkisi öğretirsin. Kayıt döngüsünde **okuma → karar → gönderme → kayıt** sırasını incelemek bu yüzden gerekir; dosya sütun adları bu ilişkiyi tek başına açıklamaz.

[Hedef takibi CSV'sinde](../simulasyon/denetleyici.md) bu ayrım açık: `q_before`, `command`, `q_after`. Gerçek teleop'ta leader isteği ile follower'a gerçekten gönderilen sınırlandırılmış komut farklı olabilir. Kayıtta hangisinin action olduğu belirtilmelidir. `max_relative_target` gibi sınırlama uygulanıyorsa öğrenme hedefini de bu farkı bilerek seç.

## 2. Kamera gecikmesi için sayısal örnek

Kontrol 30 Hz ise bir adım yaklaşık 33.3 ms'dir. Kamera içeriği karardan 100 ms daha eskiyse model yaklaşık üç adım gerideki sahneyi görür. Uç 0.10 m/s hareket ederken bu aralıkta 1 cm yol alır. Küçük bir nesnede bu fark kapanış zamanını etkileyebilir.

Her kameranın yakalama zamanı, son frame'in okunma zamanı, eklem okuma zamanı ve komut gönderme zamanını ayrı ölçmek ideal başlangıçtır. İki kamera da “30 FPS” yazıyor diye aynı anda pozlandıklarını varsayma. USB ve video kuyrukları eski frame döndürebilir.

İlk pratik kontrol: tutucuyu yavaşça aç-kapat; görüntüdeki kapanışla state/action izlerini birlikte incele. Ölçmeden bütün veri setini üç kare kaydırma. Gecikme değişkense sabit kaydırma her örneği düzeltmez; önce kayıt hattını iyileştirmek gerekir.

## 3. Hedef konum, delta ve sonraki konum

Varsayalım mevcut ölçüm `q_t=0.10 rad`, gönderilen hedef `a_t=0.16 rad`, sonraki ölçüm `q_(t+1)=0.12 rad`:

| Temsil | Değer | Anlam |
|---|---|---|
| Mutlak hedef | 0.16 rad | Servo buraya gitmeye çalışsın |
| Duruma göre hedef farkı | 0.06 rad | Mevcut ölçümden hedefe fark |
| Gerçekleşen hareket | 0.02 rad | Bu adımda ölçülen konum değişimi |

Bu üç etiketten hangisini öğreniyorsan runtime da aynı tanımı uygulamalıdır. “Altı sayı çıkıyor” kontrolü birim ve anlam uyuşmazlığını yakalayamaz. Dataset kartına joint sırası, birim, referans ve gripper aralığı ekle.

Normalizasyon bunun üstüne eklenen sayısal dönüşümdür. Örneğin ortalama `μ=0.10`, standart sapma `σ=0.05` ise mutlak hedef `0.16` model uzayında `(0.16−0.10)/0.05=1.2` olur. Model çıktısı `1.2` radyan diye gönderilmez; önce uygun istatistikle geri dönüştürülür. Normalizasyon, yanlış robot birimini fiziksel olarak düzeltmez.

## 4. Tek eylemden action chunk'a

SmolVLA'nın bu tarifteki ufku `H=50`. `t` anındaki gözlem için etiket:

```text
[a_t, a_(t+1), ..., a_(t+49)]
```

30 Hz'de ilk-son etiketin zaman farkı `49/30 ≈ 1.633 s`; 50 komutun sırayla yürütüldüğü süre `50/30 ≈ 1.667 s`. “Ufuk süresi” derken bu iki tanımdan hangisini kullandığını belirt.

Episode'da yalnız 30 frame varsa ilk gözlem için bile 50 gerçek gelecek eylem yok. LeRobot okuyucusu episode dışındaki indeksleri sınırdaki örneğe kırpar ve padding maskesi üretir. Böylece sonraki episode'dan eylem taşınmaz. [LeRobot dataset reader](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/datasets/dataset_reader.py)

## 5. Padding'i elle hesapla

Uzunluğu 4 olan bir episode ve `H=3`:

| Başlangıç | Pencere | `action_is_pad` |
|---|---|---|
| 0 | a0, a1, a2 | false, false, false |
| 1 | a1, a2, a3 | false, false, false |
| 2 | a2, a3, a3 | false, false, true |
| 3 | a3, a3, a3 | false, true, true |

Son eylemin tekrar görünmesi üç yeni gösterim olduğu anlamına gelmez. Masked kopyalar tensör şeklinin sabit kalmasını sağlar. `true` burada **geçerli** değil, **padding** demektir; ters yorumlamak en faydalı veriyi loss'tan çıkartır.

Bizim 30 frame'lik episode ve 50 adımlık ufukta gerçek etiket sayısı başlangıçlara göre `30+29+...+1=465`. Toplam yuva `30×50=1500`; `1035/1500=%69` padding. Üç aynı uzunlukta episode oranı değiştirmez.

## 6. Gerçek kayıt üzerinde çalıştır

Kendi oluşturduğun smoke kaydının yolunu kullan. Bu çalışma alanında doğrulanmış veri `data/sim-smoke-verified` altında:

```bash
.venv-ml/bin/python examples/04_inspect_dataset.py data/sim-smoke-verified
.venv-ml/bin/python examples/10_action_windows.py \
  data/sim-smoke-verified --horizon 50
```

Beklenen çıktı: `actions=[90,50,6]`, `action_is_pad=[90,50]`, `states=[90,6]`, `padded_fraction=0.69`. NPZ dosyası `outputs/action-windows.npz` olur. Sonraki deneyde yeni çıktı yolu seç:

```bash
.venv-ml/bin/python examples/10_action_windows.py \
  data/sim-smoke-verified --horizon 10 \
  --output outputs/action-windows-h10.npz
```

Script küçük veri setlerini belleğe alır. Normal çalışmada yalnız Parquet okur; normalizasyon uygulamaz, LeRobot eğitim okuyucusunun yerine geçmez. Amacı episode sınırını ve etiket şekillerini görünür kılmaktır. Büyük kayıtlar için eğitim altyapısının diskten örnekleyen okuyucusunu kullan.

`--verify-lerobot` eklersen her episode'un ilk/son örneğini gerçek `LeRobotDataset` okuyucusuyla da açar; action ve padding maskesini karşılaştırır. Bu seçenek sınır örneklerinin videolarını da PyAV ile okur. Yerel üç episode için **6/6 sınır örneği eşleşti**. Yeni bir çıktı yolu kullanarak deneyebilirsin:

```bash
.venv-ml/bin/python examples/10_action_windows.py \
  data/sim-smoke-verified --verify-lerobot \
  --output outputs/action-windows-checked.npz
```

**Alıştırma:** H=10 için geçerli yuva sayısı `21×10 + 9+8+...+1 =255`, toplam 300. Padding `%15` olmalı. Ufku azaltmak padding'i düşürür; görev başarısının otomatik artacağı sonucunu vermez.

## 7. Loss'ta doğru payda

Maskeyi hatayla çarpıp sonra bütün tensör boyutuna bölmek, çok padding olan batch'in loss'unu yapay biçimde küçültür. Geçerli zaman ve eylem boyutlarını saymalısın.

```text
loss = geçerli boyutlardaki kare hata toplamı
       / (geçerli zaman adımı sayısı × gerçek action boyutu)
```

İki geçerli adım, iki action boyutu ve kare hatalar `[1,4]`, `[9,16]` olsun. Üçüncü adım padding. Doğru ortalama `30/4=7.5`; üç adımın tamamına bölmek `30/6=5` üretir. Veri aynı olduğu halde log daha iyi görünür. Kurulu SmolVLA'nın final loss'u geçerli eleman sayısıyla bölüyor; ara tanı logları aynı paydayı kullanmayabilir. [SmolVLA loss uygulaması](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/policies/smolvla/modeling_smolvla.py)

## 8. Train/validation/test nasıl ayrılır?

Komşu frame'ler neredeyse aynı görüntü ve büyük ölçüde aynı action chunk içerir. Frame'leri rastgele bölersen aynı hareketin çok benzer kopyaları iki tarafta bulunur. Episode düzeyinde ayrım asgari başlangıçtır.

Daha kuvvetli test için grup tanımla: kayıt günü, nesne örneği, başlangıç bölgesi veya kamera düzeni. Modelin hangi tür yeniliğe dayanmasını istediğine göre test grubu seç. Aynı gün aynı masa düzenindeki farklı episode'lar “yeni ortam” testi değildir.

Örnek: 100 episode'un 70'i eğitim, 15'i model seçimi, 15'i son test. Sayılar önerilen evrensel oran değil, işleyiş örneğidir. Model ayarını 15 son test episode'una bakarak değiştirirsen o grup artık bağımsız son test değildir. `--dataset.eval_split` otomatik olarak gün/nesne bazlı ayrım kurmaz; araştırma iddiana uygun gruplamayı ayrıca tasarlamalısın.

Normalizasyon istatistikleri ideal olarak eğitim bölümünden hesaplanır. Dataset metadata'sındaki mevcut istatistiklerin hangi kapsamdan üretildiğini incele; hazır split bayrağının istatistikleri yeniden hesapladığını varsayma. Daha sıkı değerlendirmede eğitim bölümü ve preprocessing istatistikleri ayrıca sürümlenir.

## 9. Veri çeşitliliği ile veri hacmi

Bir nesneyi aynı başlangıç noktasından 100 kez almak, 100 farklı konum öğrenmek değildir. Hedef dağılımını bir tabloya dök: sol/orta/sağ, yakın/uzak, farklı kavrama yönleri, küçük ışık değişimleri. Sonra hangi hücrelerin boş olduğunu say.

Kurtarma gösteriminde uzman küçük bir sapmadan görevi başarıyla bitirmeyi gösterir. Rastgele başarısız hareketleri başarılı BC verisine karıştırmak aynı şey değildir. Başarısız episode'lar hata analizi için değerlidir; hangi eğitim hedefine dahil edileceği ayrı karardır.

**Bitirme çıktısı:** action sözleşmesi, zaman incelemesi, padding oranı, grup bazlı bölme listesi ve video kalite notları. Bunlar varsa eğitim sonucunu veriye bağlayarak tartışabilirsin.
