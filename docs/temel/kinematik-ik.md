# Kinematik, ters kinematik ve tekillik

Bu bölümün sonunda `(x, y)` hedefinden iki farklı eklem çözümü çıkaracak, ikisini ileri kinematikle doğrulayacak ve neden ikisinin de gerçek bir kol için geçerli olmayabileceğini açıklayacaksın. Ön koşul: [koordinatlar ve kontrol](robotik.md).

Hesapta kullandığımız düzlemsel iki eklemli kolun parçaları **18 cm ve 14 cm**. Bunlar bir öğretim modeli; SO-101'in link ölçüleri veya gerçek IK modeli olarak kullanılmaz.

## 1. İleri kinematik: açıdan uca

`q1` ilk parçanın x eksenine göre açısıdır. `q2` ikinci parçanın **ilk parçaya göre** açısıdır. Bu yüzden ikinci parçanın dünya açısı `q1 + q2` olur.

```text
x = L1 cos(q1) + L2 cos(q1 + q2)
y = L1 sin(q1) + L2 sin(q1 + q2)
```

`q1 = 0`, `q2 = π/2` için ilk parça sağa 18 cm, ikinci parça yukarı 14 cm uzanır. Uç `(0.18, 0.14)` metredir. İkinci terimde yalnız `q2` kullanmak, ilk parçayı döndürdüğünde yanlış sonuç verir.

Trigonometrik fonksiyonların girdisi bu Python örneklerinde radyandır. `90° = π/2 rad`; `np.sin(90)` doksan derecenin sinüsü değildir. Ekranda derece gösterebilir, hesapta radyan kullanabilirsin; dönüşümü giriş/çıkış sınırında yap.

## 2. Hedefe erişilebilir mi?

Eklem sınırları ve engelleri olmayan bu ideal modelde tabandan uca mesafe `r` için:

```text
r = sqrt(x² + y²)
abs(L1 - L2) <= r <= L1 + L2
0.04 m <= r <= 0.32 m
```

Tam açılınca 32 cm'ye erişir; tamamen katlanınca arada 4 cm kalır. `(0.40, 0.00)` hedefine erişmek için “daha çok IK iterasyonu” çözüm değildir. Fiziksel robotta eklem sınırları, gövde ve masa bu ideal alanı daha da daraltır.

## 3. Çözümlü IK: hedef (22 cm, 10 cm)

Kosinüs teoreminden ikinci açı için:

```text
c2 = (x² + y² - L1² - L2²) / (2 L1 L2)
   = (0.22² + 0.10² - 0.18² - 0.14²) / (2 × 0.18 × 0.14)
   ≈ 0.126984

q2 = ±acos(c2)
q1 = atan2(y, x) - atan2(L2 sin(q2), L1 + L2 cos(q2))
```

İki çözüm:

| Dal | q1 | q2 | FK ile geri hesaplanan uç |
|---|---|---|---|
| A | −10.6301° | +82.7046° | `(0.22, 0.10)` m |
| B | +59.5180° | −82.7046° | `(0.22, 0.10)` m |

“Dirsek yukarı/aşağı” isimleri çizdiğin eksenlere bağlıdır; iki çözümü işaretleriyle kaydetmek daha nettir. `atan2(y,x)` kullanmamızın nedeni yönün hangi bölgede olduğunu korumaktır; `atan(y/x)` tek başına bunu yapamaz.

```bash
.venv/bin/python examples/12_planar_ik.py
.venv/bin/python examples/12_planar_ik.py --x 0.18 --y 0.14
.venv/bin/python examples/12_planar_ik.py --x 0.40 --y 0
```

Son komutun hata koduyla bitmesi beklenir. Script iki çözümü FK ile `1e-12 m` sayısal toleransta kontrol eder; bu, **bu hesapta** yuvarlama doğruluğudur, fiziksel kolun konum hassasiyeti değildir.

## 4. Birden fazla çözümden hangisi?

Mevcut durum A dalına yakınsa B dalına aniden geçmek büyük hareket isteyebilir. Çözüm seçerken eklem sınırı, hareketin sürekliliği, masa/gövde çarpışması ve tutucunun yaklaşma yönü gerekir. Uç aynı noktada olsa bile kolun kapladığı hacim farklıdır.

Pratik bir seçim yaklaşımı: geçersiz dalları ele; kalanlarda mevcut açıya olan ağırlıklı uzaklığı değerlendir. Dönel açılarda `179°` ile `−179°` farkının her koşulda `358°` olmadığını da unutma; sürekli dönebilen ve mekanik sınırları olan eklemlerin davranışı ayrı değerlendirilir.

SO-101 için bu iki boyutlu formülü altı sütuna genişletmek doğru model üretmez. Gerçek eklem eksenleri, link dönüşümleri, limitler ve gripper geometrisi robot varlığından okunmalıdır.

## 5. Koordinat dönüşümü: aynı noktanın iki adı

`T_base_camera`, kamera koordinatında yazılmış bir noktayı taban koordinatına dönüştürsün:

```text
p_base = R_base_camera p_camera + t_base_camera

T = [ R(3×3)  t(3×1) ]
    [ 0 0 0      1    ]
```

Örneğin kameranın yönü tabanla aynı, merkezi tabanda `(0.10, 0.00, 0.30)` m olsun. Kamera koordinatındaki `(0.02, 0.03, 0.40)` m noktası tabanda `(0.12, 0.03, 0.70)` m olur. Bu yalnız dönüşüm aritmetiği örneğidir; masaya bakan gerçek kameranın yönü genelde böyle değildir.

Ters yönde kullanmak için yalnız `t` işaretini değiştirmek genel olarak yetmez:

```text
R_inverse = Rᵀ
t_inverse = -Rᵀ t
```

Dönüşümleri zincirlerken aradaki frame isimleri eşleşmeli: `T_base_camera × T_camera_object = T_base_object`. Kameranın konumunu bilmek, nesnenin kamera içindeki derinliğini otomatik olarak vermez. [Kamera bölümü](../donanim/kamera-kalibrasyonu.md) bu eksik ölçümü ele alır.

## 6. Jacobian: küçük hareketin etkisi

Küçük eklem değişimi için `Δp ≈ J(q) Δq`. Bu modelde türev alırsak:

```text
J = [ -L1 sin(q1)-L2 sin(q1+q2)   -L2 sin(q1+q2) ]
    [  L1 cos(q1)+L2 cos(q1+q2)    L2 cos(q1+q2) ]
```

Yukarıdaki A çözümünde:

```text
J ≈ [ -0.100000  -0.133204 ]  metre/radyan
    [  0.220000   0.043089 ]
```

`Δq = (0.01, 0)` rad için uç yaklaşık `(-0.001, 0.0022)` m değişir: sola 1 mm, yukarı 2.2 mm. Büyük açı değişiminde bu doğrusal yaklaşımı tek adımda kullanmak hata üretir. Küçük adımlarla yeniden hesaplamak gerekir.

Script analitik Jacobian'ı merkezi sonlu farkla da denetler: bir eklemi `+ε` ve `−ε` oynatıp FK farkını `2ε`'a böler. Bu iki bağımsız hesap arasındaki uyum türevdeki işaret hatasını yakalar.

## 7. Tekillik neden sorun çıkarır?

Kol düz açıldığında `q2=0` olur. `det(J)=L1 L2 sin(q2)` sıfırdır. Uç, o anda bazı yönlerde birinci dereceden hareket üretemez. Bu geometrik sınırda küçük bir uç isteğine karşı çok büyük açı değişimi hesaplanabilir.

Sayısal IK, uç hatasını Jacobian üzerinden eklem düzeltmesine çevirir. Kare olmayan veya tekil matrisler için sıradan ters yerine pseudoinverse kullanılabilir; başlangıç tahmini sonucu etkiler. [Modern Robotics: sayısal IK](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-1-of-2/)

Sönümlü en küçük kareler için yaygın güncelleme biçimini şu optimizasyondan okuyabilirsin:

```text
min_Δq ||J Δq - e||² + λ² ||Δq||²
Δq = Jᵀ (J Jᵀ + λ² I)⁻¹ e
```

İlk terim uç hatasını azaltır, ikinci terim büyük eklem adımını cezalandırır. `λ` büyüdükçe düzeltme daha tutucu olur; bu birimlere bağlı sayısal ayardır. Hesapta açık matris tersi oluşturmak yerine doğrusal sistemi çözmek tercih edilir. Sönüm eklemek erişilemeyen hedefi erişilebilir yapmaz; ayrıca eklem limiti veya çarpışma kontrolü yerine geçmez.

## 8. VLA varken IK neden öğreniyoruz?

Eklem eylemi üreten VLA'nın her adımda senin yazdığın analitik IK'yı çağırması şart değildir. Ancak veri üretirken, görev sınırını seçerken ve yanlış hareketi incelerken geometri gerekir. Model masanın altına uzanıyorsa kamera dönüşümü mü yanlış, hedef mi erişilemez, yoksa action birimi mi bozuk sorularını ayırabilmelisin.

**Alıştırma:** `--x 0.32 --y 0` çalıştır. İki çözümün birleşmesini ve en küçük tekil değerin sıfıra yaklaşmasını açıkla. Ardından hedefi 1 cm daha uzağa taşı; sonucu eğitim eksikliğiyle değil erişim hesabıyla açıklayabilmelisin.
