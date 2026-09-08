# Kamera geometrisi ve kalibrasyon

VLA'nın görüntü kullanması, bütün piksel hatalarının eğitimde kendiliğinden çözüleceği anlamına gelmez. Kamera düzenini yeniden kurabilmek, nesnenin ne zaman ve nerede göründüğünü bilmek gerekir. Geometrik nesne konumlandırma veya sim/gerçek kamera eşlemesi yapacaksan bu bölüm doğrudan işe yarar.

## 1. Dört ayrı kalibrasyon işi

| İş | Ne eşler? | Çıktı örneği |
|---|---|---|
| Servo kalibrasyonu | Motor okuması ↔ eklem referansı/aralığı | Motorlara ait offset ve sınırlar |
| Kamera iç kalibrasyonu | Kamera içindeki 3B ışın ↔ piksel | `K`, distorsiyon katsayıları |
| Kamera dış kalibrasyonu | Kamera frame'i ↔ robot/masa frame'i | `R`, `t` veya `T` |
| Öğrenme normalizasyonu | Dataset değerleri ↔ modelin sayısal ölçeği | Ortalama, standart sapma |

Kamera matrisi bulmak motorların doğru yönde döndüğünü kanıtlamaz. Model normalizasyonu da kamera koordinatını robot koordinatına dönüştürmez.

## 2. Bir nokta hangi piksele düşer?

İdeal pinhole modelinde kamera koordinatındaki nokta `(X,Y,Z)` ve `Z>0` için:

```text
u = fx × X/Z + cx
v = fy × Y/Z + cy

K = [ fx   0  cx ]
    [  0  fy  cy ]
    [  0   0   1 ]
```

`fx, fy` piksel ölçeğinde odak parametreleri; `cx, cy` ana nokta koordinatıdır. Gerçek lens distorsiyonu ayrıca modellenir. OpenCV'nin kalibrasyon işlevleri bilinen hedef noktaları ile görüntü noktalarından bu parametreleri kestirir. [OpenCV kamera modeli](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html)

**Hesap örneği:** `fx=fy=600`, `cx=320`, `cy=240`, nokta `(0.05, −0.02, 0.50)` m olsun. `u=380`, `v=216` piksel çıkar. Aynı ışında `(0.10, −0.04, 1.00)` m noktası da aynı piksele düşer. Tek RGB pikselinden hangi derinlikte olduğunu bu modelle bilemezsin.

Derinlik için masa düzlemi gibi ek varsayım, bilinen nesne geometrisi/ölçeği, çoklu görüş veya derinlik sensörü gerekir. “Kamerada küpün merkezi `(380,216)`” bilgisi tek başına robota gönderilecek `(x,y,z)` değildir.

## 3. Kamera ile robot eksenleri

OpenCV kamera modelinde yaygın ifade x sağa, y görüntüde aşağı, z kameranın önüne doğrudur. Robotun taban eksenleri ve MuJoCo kamera bakış sözleşmesi farklı olabilir. Eksenlerin adını aynı yazmak dönüşümü doğru yapmaz. Bir test noktası seçip her frame'deki sayısal karşılığını doğrula. [OpenCV projeksiyon ve extrinsic tanımları](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html)

`solvePnP` ile nesne/hedef noktalarından bulunan dönüşümün yönünü dikkatle oku: nesne koordinatını kameraya taşıyan dönüşüm, aradığın kamera-tabana dönüşümle aynı şey olmayabilir. Dosyada `extrinsics.json` yerine `T_base_camera` gibi yönü açık anahtar kullan.

**Mini kontrol:** tabanda bilinen bir noktayı kameraya dönüştür, `projectPoints` ile görüntüye taşı ve gerçek görüntüde işaretle. Noktalar sistematik ters yönde kayıyorsa önce frame yönünü ve matris çarpım sırasını incele.

## 4. İç kalibrasyon toplama tarifi

Örneğin 9×6 **iç köşeli**, kare kenarı 20 mm olan bir hedef kullanacaksan yazdırılmış geometrinin gerçekten bu ölçüde olduğunu ölç. 9×6 kare ile 9×6 iç köşe aynı desen değildir. Hedefi düz bir yüzeye sabitle; dalgalanan kağıt ölçüm modelini bozar.

Başlangıç çalışması olarak 15–25 farklı görüntü toplayabilirsin; bu bir evrensel yeterlilik sayısı değildir. Hedefi merkezin yanında kenarlarda da göster, çeşitli eğimler ve mesafeler kullan. Arka arkaya aynı pozun yirmi karesi geometri çeşitliliği sağlamaz. Hareket bulanıklığını ve otomatik odak değişimini kontrol et.

OpenCV tarafındaki akış: köşeleri bul, alt piksel düzeltmesi uygula, bilinen düzlem noktalarıyla eşle, `calibrateCamera` ile çöz. Sonuçları yeniden projeksiyonla incele. [OpenCV kalibrasyon öğreticisi](https://docs.opencv.org/4.13.0/dc/dbb/tutorial_py_calibration.html)

Burada gerçek kamera bağlı olmadığı için uydurulmuş `K` dosyası verilmez. Yukarıdaki 600 piksellik odak yalnız hesap örneğidir. Kendi kameranın değerlerini bu örnekten kopyalamamalısın.

## 5. Düşük reprojection error yeterli mi?

Reprojection error, bildiğin 3B hedef noktalarını tahmin edilen modelle görüntüye yansıttığında ölçülen köşelerden ne kadar uzak düştüğünü özetler. Birim pikseldir. Ortalama düşükken birkaç kötü görüntü, kenarlarda sistematik hata veya yanlış kare ölçeği saklanabilir.

Ortalamanın yanında görüntü başına hata ve en kötü görüntüleri incele. Çözümde kullanılmamış birkaç hedef pozu üzerinde de doğrula. Tüm hedef noktalarını yanlışlıkla 20 mm yerine 25 mm ölçekle tanımlarsan görüntüye uyum iyi kalabilir; fiziksel çeviri mesafesi yanlış ölçeklenir. Piksel uyumu, metre ölçeğinin doğru olduğunu tek başına kanıtlamaz.

## 6. Resize ve crop neden K'yı değiştirir?

Distorsiyonsuz örnekte 640×480 görüntüyü yarıya indirirsen odak ve ana nokta piksel değerleri de yarılanır:

```text
fx'=300, fy'=300, cx'=160, cy'=120
(380,216) → (190,108)
```

Sonra soldan 40, üstten 20 piksel kırparsan yeni ana nokta `(120,100)` olur. Önce kırpıp sonra küçültmek farklı sayı verir; işlem sırası kaydedilmelidir. Model kare görüntü isterken boşluk ekliyorsan, eklenen sol/üst padding de ana noktaya eklenir.

Genel, saf resize → crop → pad hesabı:

```text
fx' = sx fx        fy' = sy fy
cx' = sx cx - crop_left + pad_left
cy' = sy cy - crop_top  + pad_top
```

Lens distorsiyonunu giderirken kullanılan yeni kamera matrisi varsa sonraki dönüşümü o matrisle başlat. VLA yalnız piksel girdisi kullanıyorsa sen bu `K` hesabını runtime'da kullanmayabilirsin; fakat geometrik noktalar ile yeniden boyutlanmış görüntüyü birlikte kullanıyorsan gerekli olur.

## 7. Sabit kamera ve bilek kamerası

Sabit kameranın `T_base_camera` dönüşümü, kamera montajı değişmediği sürece sabit kabul edilebilir. Bilek kamerasında tabana göre dönüşüm eklem konumuyla değişir:

```text
T_base_camera(q) = T_base_wrist(q) × T_wrist_camera
```

Robot hareketlerini ve kalibrasyon hedefi gözlemlerini birlikte kullanarak kamera-robot bağlantısını kestirmek hand-eye kalibrasyon problemidir. OpenCV bu problem için `calibrateHandEye` sunar; giriş/çıkış dönüşüm yönleri API sözleşmesinden kontrol edilmelidir. [Hand-eye API](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html#gaebfc1c10372d17a83f7a3296b952c86b)

Pratikte ilk iş, iki kamera adını sabitlemek ve sahnedeki rollerini kaydetmektir: `front` çalışma alanını, `wrist` yaklaşma/kapanışı görsün. Gösterim sırasında wrist görüntüsü sürekli tutucu tarafından kapanıyorsa eğitime daha çok aynı kareyi eklemek görünmeyen nesneyi görünür yapmaz.

## 8. VLA için mutlaka geometrik kalibrasyon gerekir mi?

Görüntü ve eklem gösterimlerinden doğrudan eklem eylemi öğrenen bir hat, açık `K` veya `T` matrisi olmadan kurulabilir. Bu, kamera düzeninin önemsiz olduğu anlamına gelmez. Eğitimde ve çalıştırmada farklı kamera yüksekliği, görüş alanı, crop, odak ve pozlama modelin gördüğü dağılımı değiştirir.

İlk VLA deneyi için kamera geometrisinin bütün araştırma ayrıntılarını bitirmen gerekmez. Önce sabit ve tekrar kurulabilir bir düzen, nesneyi yeterince gösteren görüşler ve doğru zaman hizalaması sağla. Nesne konumunu analitik çıkarmaya veya kamera sim eşlemesi yapmaya başladığında iç/dış kalibrasyonu ölçerek ekle.

## 9. Saklayacağın kamera kartı

`templates/camera-card.json` dosyasını kopyalayıp doldur. Çözünürlük, FPS, aygıt kimliği, pozlama/odak davranışı, montaj fotoğrafının yolu, birimler, dönüşüm yönü ve kalibrasyon tarihi birlikte dursun. Boş alanları tahminle doldurma.

**Bitirme koşulu:** kamerayı söküp tekrar kurduğunda referans görüntüyü karşılaştırabiliyor; farklı crop ile aynı `K` kullanmanın neden yanlış olduğunu sayılarla açıklayabiliyorsun. Fiziksel kalibrasyon tamamlandı demek için kendi kamerandan ölçüm ve doğrulama görüntüleri gerekir.
