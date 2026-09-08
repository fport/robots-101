# Koordinatlar ve kontrol

Bir kolu kontrol etmek için üç soruyu ayır: “hangi pozu istiyorum?”, “bu poz için hangi eklemler nerede olmalı?” ve “motorlar o hedefe nasıl yaklaşmalı?”. İlk soru görev, ikincisi kinematik, üçüncüsü kontroldür.

## Eklemler ve uç nokta

Eklem vektörünü `q = [q1, q2, q3, q4, q5, gripper]` diye yazabiliriz. Bu, altı sayının aynı fiziksel birimde olduğu anlamına gelmez. Döner eklem radyan/derece ya da normalize aralıkta, tutucu da ayrı bir normalize aralıkta temsil edilebilir.

**İleri kinematik (FK):** eklem değerlerinden uç noktanın konumunu hesaplama. **Ters kinematik (IK):** istenen uç konumundan uygun eklem değerlerini bulma. IK'nin birden çok çözümü veya hiç çözümü olabilir. Eklem limitleri, yaklaşım açısı ve engeller çözüm seçiminde etkilidir.

İki boyutlu, iki eklemli bir eğitim kolunda:

```text
x = L1*cos(q1) + L2*cos(q1 + q2)
y = L1*sin(q1) + L2*sin(q1 + q2)
```

İkinci çubuğun dünya açısı `q1 + q2` olur; `q2` birinci çubuğa göre açıdır. [İnteraktif laboratuvarda](laboratuvar.md) bu ilişkiyi gör. Bu iki çubuklu hesap SO-101'in tam kinematik modeli değildir.

## Referans çerçevesi

`x=0.2, y=0.1, z=0.05` yazdığında “hangi koordinat sisteminde?” sorusu cevaplanmış olmalı. Dünya/masa, robot tabanı, tutucu ve kamera ayrı çerçevelerdir. Kamera görüntüsündeki piksel konumu metre değildir. Bir pikseli dünyadaki noktaya taşımak kamera kalibrasyonu, derinlik veya bilinen bir yüzey varsayımı gerektirir.

Homojen dönüşümün `T_world_camera` gibi bir adı, yönünü açıklar: kameradaki bir noktanın dünya koordinatını elde etmek için kullanılır. Dönüşümün tersini yanlış yerde kullanmak, işaret hatası gibi görünen büyük konum hataları üretir. Matrisin yanı sıra birim, eksen yönleri ve dönüş sırası da yazılmalıdır.

## Ölçülen durum ve verilen hedef

```text
observation.state[t] = o an ölçülen eklem konumları
action[t]            = o durumdan sonra gönderilen motor hedefleri
observation.state[t+1] = fizik ve kontrol sonucunda ulaşılan durum
```

Hedef anında gerçekleşmez. Motor gecikmesi, yük ve kontrol döngüsü araya girer. Veri setine `action[t]` yerine aynı anın `state[t]` değerini yazarsan gerçek komutu kaybetmiş olabilirsin. Öğrenci modelin öğreneceği ilişki yanlışlaşır.

## Birimler

| Gösterim | Örnek | Yanlış varsayım |
|---|---|---|
| Metre | `0.10` = 10 cm | `10` yazıp 10 cm beklemek |
| Radyan | π/2 ≈ 1.571 = 90° | `90`'ı radyan olarak göndermek |
| Normalize motor hedefi | Kalibrasyona bağlı aralık | Her robotta aynı fiziksel açı sanmak |
| Quaternion | MuJoCo'da sık kullanılan sıra `w,x,y,z` | Başka API'nin `x,y,z,w` sırasını aynen geçirmek |
| RGB görüntü | Kanal sırası R,G,B | OpenCV BGR verisini dönüştürmeden kullanmak |

MuJoCo model tanımındaki açılar `compiler` ayarına bağlı olabilir; runtime döner eklem değerleri radyandır. `geom size` gibi alanlarda da kutunun yarı boyutları söz konusu olabilir. [MuJoCo XML referansı](https://mujoco.readthedocs.io/en/stable/XMLreference.html) API'nin birim ve şekil sözleşmesini kontrol edeceğin yerdir.

## Üç zaman ölçeği

Fizik adımı örneğin `0.002 s` ise motor 500 fizik adımı/s çalışır. Kontrol hedefini 30 Hz'de güncellemek yaklaşık her `0.0333 s`'de yeni action anlamına gelir. Kamera ise başka FPS'te çekiyor olabilir. Bunlar aynı sayaç değildir.

`0.0333 / 0.002 = 16.67`; tam sayı olmayan oranlarda simülatörün alt adım zamanlamasını kontrol et. `step(30)` otomatik olarak bir saniye demek değildir. Veri setinin `fps` değeri kaydedilen kontrol örneklerinin zamanını temsil etmelidir.

## Basit kapalı döngü

Bir pozisyon kontrolcü, `hata = hedef - ölçüm` ilişkisini kullanır. P kontrol büyüyen hataya daha büyük düzeltme üretir. D terimi hareketi sönümleyebilir. Kazançları yükseltmek her zaman daha iyi sonuç vermez; salınım ve temas kuvveti artabilir. Önce [tek eklem deneyinde](../simulasyon/mujoco.md) hedefi değiştirip zaman cevabını incele.

Bir `qpos` ataması simülasyonda robotu ışınlar. Bir aktüatör hedefi fizik motorunun kolu o hedefe götürmesini ister. IK sonucunu ekrana çizmek için ilkini, dinamik davranışı ve demonstrasyonu incelemek için ikincisini seçersin. Işınlanan “kavrama” fiziksel bir kavrama gösterimi değildir.
