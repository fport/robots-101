# Çözümlü sınama defteri

Önce cevabı kendin yaz; ardından çözümü aç. Amaç terim ezberi değil, robotik deneyinde yanlış sonuca götürecek varsayımları fark etmek. İlgili bölümler [derin okuma rotasında](../basla/derinlik.md).

## 1. Altı sayı, altı serbest yönelim mi?

SO-101 politikasının action şekli `[6]`. Ucun x/y/z ve roll/pitch/yaw değerlerini bağımsız seçebilir misin?

??? success "Çözüm"
    Hayır. Altı bileşenin biri tutucu açılışıdır; kolun beş dönel eklemi vardır. Altı boyutlu serbest uç pozu genel olarak bağımsız sağlanamaz. Ayrıca erişim, eklem limitleri ve çarpışmalar gerekir. Action boyutu ile uç görev uzayı aynı kavram değildir.

## 2. Radyan mı normalize mi?

Simde bir ekleme `0.5` yazdın. Gerçek kolda `use_degrees=false` kullanılan tarifte de `0.5` yazınca aynı açı oluşur mu?

??? success "Çözüm"
    Bunu sayının aynı olmasından çıkaramazsın. İncelenen sim varlığında radyan hedef, donanım tarifinde normalize ölçek kullanılır. Eklem sırası, sıfır, yön ve aralık eşlemesi gerekir. Derece seçeneğinin kapalı olması “radyan açık” demek değildir.

## 3. Fizik ve kontrol saati

Fizik adımı 0.002 s. 50 Hz kontrol için kaç alt adım gerekir? `send_action(n_substeps=10)` ardından `step(10)` çağırırsan ne olur?

??? success "Çözüm"
    Kontrol periyodu 1/50=0.020 s; 10 alt adım gerekir. İkinci çağrıyla toplam 20 alt adım, yani 0.040 s ilerletirsin. Döngüyü hâlâ 50 Hz diye etiketlemek gerçek sim zamanını yanlış anlatır.

## 4. Komut ulaştı, kol ulaştı mı?

Son referans hedefe eşit, fakat ölçülen eklem konumu 0.08 rad uzakta. Tolerans 0.04 rad. Aşamayı tamamlayabilir misin?

??? success "Çözüm"
    Hedef takip sözleşmesine göre hayır. Referansın hedefe eşit olması servonun o hedefi gerçekleştirdiğini kanıtlamaz. Ölçülen hata tolerans içinde ve gereken ardışık ölçüm sayısı boyunca uygun olmalıdır.

## 5. İki IK çözümü

18 ve 14 cm'lik düzlemsel kolda `(22,10)` cm hedefi için iki çözüm var. Neden birini rastgele seçmiyoruz?

??? success "Çözüm"
    İki çözüm aynı uca rağmen farklı kol yerleşimi üretir. Mevcut pozdan uzaklık, eklem limiti, masa/gövde çarpışması ve yaklaşma yönü farklıdır. Sayısal çözümler yaklaşık `(−10.6301°,82.7046°)` ve `(59.5180°,−82.7046°)`. Bu ideal model SO-101 IK'sı değildir.

## 6. Bir piksel, iki derinlik

Kamera içindeki `(0.05,0.02,0.50)` ve `(0.10,0.04,1.00)` noktaları aynı piksele düşebilir mi?

??? success "Çözüm"
    İdeal pinhole modelinde evet; X/Z ve Y/Z oranları aynıdır. Tek piksel bir ışını tanımlar. Derinlik için ek bilgi gerekir; yalnız kamera matrisini bilmek nesneye olan mesafeyi çözmez.

## 7. Kamera matrisi ve resize

640×480 görüntüde `fx=600`, `cx=320`. Görüntü önce yarıya küçültülüp sonra soldan 40 piksel kırpılıyor. Yeni değerler?

??? success "Çözüm"
    Resize sonrası `fx=300`, `cx=160`; crop sonrası `fx=300`, `cx=120`. Crop yön ve miktarı ana noktayı değiştirir. Geometrik projeksiyonu eski K ile sürdürmek yanlış piksel hesabı verir.

## 8. Etiket hangi sayı?

Ölçülen mevcut konum 0.10, gönderilen mutlak hedef 0.16, sonraki ölçüm 0.12 rad. Mutlak hedef BC etiketi, hedef delta ve gerçekleşen hareket nedir?

??? success "Çözüm"
    Sırasıyla 0.16, 0.06 ve 0.02 rad. Farklı öğrenme problemleri tanımlarlar. `o_t → a_t` mutlak hedef tarifinde etiket 0.16'dır; sonraki ölçümü hedefmiş gibi değiştirmek aynı problem değildir.

## 9. Kısa episode, uzun chunk

30 karelik episode'da her başlangıç için 50 adımlık action chunk hazırlanıyor. Padding oranı?

??? success "Çözüm"
    Geçerli adımlar `30+29+...+1=465`; toplam `30×50=1500`. Padding `1035/1500=%69`. Üç böyle episode yine %69 üretir. Örneklerin başka episode'a taşınmaması ve padding maskesinin loss'ta kullanılması gerekir.

## 10. Maskeli loss'un paydası

Kare hatalar iki geçerli adımda `[1,4]` ve `[9,16]`. Üçüncü adım padding. Maskeyi çarptıktan sonra altı elemana bölmek doğru mu?

??? success "Çözüm"
    Hayır. Toplam 30'u dört geçerli elemana bölmek gerekir: 7.5. Altıya bölmek 5 üretir ve padding oranı yüksek batch'i yapay olarak daha iyi gösterir. `action_is_pad=true` geçersiz zaman demektir.

## 11. Flow matching'deki t

`A=[0.2,−0.4]`, `ε=[1.0,0.6]`, `t=0.75` için ara örnek ve hedef alan? Çıkarımda zaman hangi yönde ilerler?

??? success "Çözüm"
    `x_t=(1−t)A+tε=[0.8,0.35]`; `u=ε−A=[0.8,1.0]`. Bu uygulamada t=1 gürültü, t=0 veridir; Euler adımı negatiftir. Bu t robotun kontrol saati değildir.

## 12. İki ayrı adım sayısı

`num_steps=10`, `chunk_size=50`, kontrol 30 Hz. Üretim ve yürütme açısından bu sayılar ne söyler?

??? success "Çözüm"
    Bir action chunk üretirken akış çözücüsü 10 güncelleme yapar. Chunk 50 robot komutu içerir; tamamının yürütülmesi yaklaşık 1.67 s'yi kapsar. Model çıkarımının 10/30 s süreceğini bu sayılardan hesaplayamazsın; donanımda ölçmelisin.

## 13. Batch yarıya indi

24.000 eğitim frame'i, batch=8, 20.000 güncelleme için kaba epoch eşdeğeri kaç? Batch=4 olursa?

??? success "Çözüm"
    İlki `160.000/24.000≈6.67`, ikincisi `80.000/24.000≈3.33`. Sampler ve filtreler gerçek kullanım dağılımını etkiler. Aynı step sayısı, batch değiştiğinde aynı veri maruziyeti değildir.

## 14. Validation mükemmel, yeni gün kötü

Frame'leri rastgele %80/%20 ayırdın. Validation çok iyi, ertesi gün görev başarısı kötü. İlk neyi incelersin?

??? success "Çözüm"
    Komşu frame/chunk sızıntısını ve günler arasındaki görüntü/başlangıç farkını. Episode düzeyinde ayrım yap; iddian yeni güne genellemekse gün bazlı ayrı test kur. Normalizasyon istatistiklerinin hangi bölümden hesaplandığını da kontrol et. Bu gözlem tek başına daha büyük model gerektiğini göstermez.

## 15. %70'ten %80'e çıktı

İki checkpoint 20'şer denemede 14 ve 16 başarı verdi. İkinci kesin daha iyi mi?

??? success "Çözüm"
    Bu örnekle kesinlik iddiası güçlü olmaz. Aynı koşullar, deneme sayısı, hata türleri ve belirsizlikle raporla. Tekrarlı, önceden belirlenmiş değerlendirme yap. Başarı yüzdesi artışı faydalı bir gözlem; tek başına geniş genelleme kanıtı değil.

## 16. Mock veri neden yetmez?

Kamera videosu, altı action sütunu ve düzgün timestamp içeren 100 mock episode ürettin. SmolVLA neden başarılı kavrama öğrenmek zorunda değil?

??? success "Çözüm"
    Şema doğruluğu davranış uzmanlığı değildir. Mock eylemler nesneyi kavrayan bir strateji göstermiyorsa modelin taklit ettiği etiketler başarılı kavramayı öğretmez. Önce uzman kontrol/teleop gösterimi ve ayrı görev başarısı ölçütü gerekir.

## Kendi proje sorunu yaz

Kendi görevinden bir başarısız video seç. “Model kötü” yerine bir gözlem, iki alternatif hipotez ve bunları ayıracak tek deney yaz. Örnek: “Tutucu nesnenin önünde kapanıyor; kamera gecikmesi veya eğitimde dar konum dağılımı olabilir; sabit konumda farklı hareket hızlarıyla zaman izini karşılaştıracağım.”

On altı cevabı okuyup onaylamak yerine en az dört hesabı terminalde yeniden üret: IK, SO-101 hedef takibi, action window ve flow matching scriptleri. Sonuçların neden aynı veya farklı olduğunu deney defterine yaz.
