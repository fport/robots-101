# Gösterim üretimi ve kayıt

Simülasyon verisi robot beklerken kayıt/eğitim yazılımını öğrenmeni sağlar. Ama öğrenilecek davranışın kalitesi, kayıt kaynağına bağlıdır: rastgele hareket, kural tabanlı uzman ve insan gösterimi birbirinden farklı öğretmenlerdir.

## Üç veri türünü ayır

| Kaynak | Ne için kullanılır? | Sınırlama |
|---|---|---|
| Mock/rastgele hareket | Şema, video, episode sınırı, dosya hattı deneyi | Başarılı görev davranışı öğretmez |
| Scripted/IK uzman | Tanımlı görevde kontrollü gösterimler | Temas ve başarı ölçütü gerçekten doğrulanmalı |
| İnsan teleoperasyonu | Görev çözme davranışını örneklemek | Operatör kalitesi ve kayıt düzeni önemlidir |

Robot yokken ilkini çalıştır; sonra güvenilir bir uzman veya hazır kaliteli veriyle eğitim alıştırmasına geç. Görsel olarak güzel bir hareketi “uzman” diye etiketlemek yeterli değildir.

## Çalışan kayıt deneyi

```bash
.venv-ml/bin/python examples/03_record_sim.py
.venv-ml/bin/python examples/04_inspect_dataset.py data/sim-smoke --expected-episodes 3
```

İlk komut varsayılan olarak 3 × 30 kontrol adımı, yani 90 örnek kaydeder. `front` kamerası 256×256, kayıt ve kontrol frekansı 30 olarak seçilmiştir. `data/sim-smoke` zaten varsa script durur; başka deneme için yeni klasör seç:

```bash
.venv-ml/bin/python examples/03_record_sim.py --root data/sim-smoke-02 --episodes 4 --steps 60
```

`ATOLYE_README.json` verinin mock kaynaklı ve yalnız veri hattını sınamak için olduğunu kaydeder. Bunu bir kavrama başarı veri seti diye yorumlama.

## Episode sınırı neden önemli?

Üç gösterimi arka arkaya çalıştırıp yalnız en sonda diske yazarsan tek uzun episode elde edebilirsin. Bu, reset noktasındaki ani konum değişimini bir görev eylemi gibi gösterebilir. Script her rollout sonunda `save_episode()` çağırır; en sonda `stop_recording()` ile dosyaları sonlandırır.

Denetim gerçek parquet içindeki episode/frame kayıtlarını sayar. Beklenen üç episode yerine tek episode varsa, terminalde “3 deneme tamamlandı” yazması veri bütünlüğünü kurtarmaz. [Strands kayıt API'si ve episode sınırları](https://github.com/strands-labs/robots/blob/main/docs/recording.md)

## Kayıt FPS ve fizik zamanı

Kaydediciye `fps=30` verirken rollout'a da `control_frequency=30` veriyoruz. Veri timestamp'leri bu sözleşmeye dayanır. Bu eşleşme zorunlu bir başlangıçtır; fizik alt adımı yuvarlaması yüzünden gerçek sim zamanı ayrıca izlenmelidir.

Bu makinedeki 30 adımlık SO-101 denemesinde raporlanan sim zamanı yaklaşık **1,02 s** oldu. `0.002 s` fizik adımıyla 30 Hz tam bölünmediği için bunu kaydet: “30 FPS yazdım, fizik tam 1,000 saniye ilerledi” sonucu çıkarma. Hassas sim/gerçek zaman eşleşmesi için ortak frekans ve alt adım stratejisi doğrulanmalı.

## Görüntüyü de kontrol et

Parquet denetimi bütün video karelerini decode etmez. `meta/info.json` içindeki kamera anahtarları ile video dosyalarının bulunduğunu doğrula; bir episode'u baştan sona izle. Donmuş görüntü, yanlış kamera ve geç gelen frame, sayısal olarak temiz bir dataset içinde saklanabilir.

Kayıt sırasında video encoder hatası varsa önce küçük bir denemeyi düzelt. Saatlerce gösterim toplayıp en sonda dosyaların açılmadığını öğrenmek yerine 3 kısa episode ile uçtan uca okuma yap.

## VLA için sim veriyi nasıl ilerletirsin?

Önce görev sabit olsun: aynı nesne, tek hedef bölgesi, sınırlı başlangıç varyasyonu. Uzman denetleyiciyi çoklu seed ile çalıştır; başarılı/başarısız sonuçları ayrı tut. Yalnız başarılı gösterimlerle ilk BC baseline'ını eğit. Testte görülmemiş başlangıçlar kullan.

Sonra tek tek ışık, renk, nesne konumu ve sürtünme değiştir. Görüntü augmentasyonu eylem etiketini değiştirmemeli. Nesneyi görselde başka yere taşıyıp action'ı aynı bırakmak çoğu görevde fiziksel olarak yanlış eğitim çifti yaratır.

Tam SmolVLA hattı [eğitim bölümünde](../ogrenme/smolvla.md). O komuta mock veriyi vermek teknik bir eğitim denemesi olabilir; başarı iddiası üretmez.
