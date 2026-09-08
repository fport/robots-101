# İnteraktif laboratuvar

Burada Python kurmadan üç kavramı deneyebilirsin. Hesaplar tarayıcıda yapılır; fizik sunucusu veya robot bağlantısı yoktur. **Aşağıdaki iki eklemli çizim bir SO-101 dijital ikizi veya MuJoCo simülasyonu değildir.**

## 1. İki eklem, bir uç nokta

İlk bağlantı 18 cm, ikinci bağlantı 14 cm. `q2`, birinci bağlantıya göre açıdır. Önce `q2=0` yap, sonra `q1`'i değiştir; iki bağlantının birlikte döndüğünü göreceksin. Sonra `q1` sabitken `q2`'yi değiştir.

<div class="lab-panel" id="kinematics-lab">
<svg viewBox="0 0 480 320" role="img" aria-label="İki eklemli düzlemsel eğitim kolu">
<defs><pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="#274149" stroke-width="0.7"/></pattern></defs>
<rect width="480" height="320" fill="url(#grid)"/>
<path d="M30 245H455M240 295V20" stroke="#6b8c91" stroke-width="1" stroke-dasharray="4 5"/>
<text x="446" y="263" fill="#a7c4c5" font-size="13">x</text><text x="252" y="28" fill="#a7c4c5" font-size="13">y</text>
<polyline id="arm-links" points="240,245 310,160 330,80" stroke="#73edd0" stroke-width="15" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
<circle cx="240" cy="245" r="12" fill="#e4efeb"/><circle id="elbow-dot" cx="310" cy="160" r="11" fill="#ffa568"/><circle id="tip-dot" cx="330" cy="80" r="8" fill="#e4efeb"/>
<text x="15" y="307" fill="#a7c4c5" font-size="11">DÜZLEMSEL FK · L₁ 18 cm · L₂ 14 cm · fizik ve çarpışma yok</text>
</svg>
<div class="lab-controls">
<label for="joint-a">Omuz açısı q₁ (derece)<input type="range" id="joint-a" min="-20" max="160" value="65"></label>
<label for="joint-b">Dirsek açısı q₂ (derece)<input type="range" id="joint-b" min="-150" max="150" value="-55"></label>
</div>
<div class="lab-result" id="arm-result" aria-live="polite"></div>
</div>

**Deney:** kolu düzleştirdiğinde erişim 32 cm olur. Katladığında uç tabana yaklaşır. Aynı uç noktasına farklı eklem açılarından ulaşma fikrini düşün; IK'nin neden tek bir cevap vermeyebildiğini açıkla. Bu çizim eklem/masa çarpışmalarını hesaba katmaz.

## 2. Ne kadar veri toplayacaksın?

640×480 RGB görüntü varsayımıyla ham depolamayı ve net gösterim süresini hesapla. İki kamera, action satırlarını ikiye katlamaz; her zaman adımında iki ayrı görüntü olur.

<div class="lab-panel" id="dataset-planner">
<div class="lab-controls">
<label for="episodes">Episode sayısı<input type="number" id="episodes" min="1" value="50"></label>
<label for="seconds">Episode süresi (s)<input type="number" id="seconds" min="1" value="20"></label>
<label for="fps">Kayıt FPS<input type="number" id="fps" min="1" value="30"></label>
<label for="cameras">Kamera sayısı<input type="number" id="cameras" min="1" value="2"></label>
</div>
<div class="lab-result" id="dataset-result" aria-live="polite"></div>
</div>

**Deney:** 50 episode × 20 saniye × 30 FPS = 30.000 zaman adımı. Reset için her episode sonrasında 20 saniye harcarsan toplam masa süresi yaklaşık iki katına çıkar. Kamera kare sayısını eğitimdeki bağımsız görev sayısıyla karıştırma; birbirine çok benzeyen 600 ardışık kare, 600 ayrı başarılı gösterim değildir.

## 3. Eylem dizisi ve gecikme

Bir VLA her model çağrısında birden fazla gelecek eylem tahmin edebilir. Diziden kaç eylem yürüttüğün, yeniden ne zaman gözlem aldığını etkiler.

<div class="lab-panel" id="chunk-lab">
<div class="lab-controls">
<label for="control-hz">Kontrol frekansı (Hz)<input type="range" id="control-hz" min="5" max="60" value="30"></label>
<label for="chunk-steps">Yürütülen eylem sayısı<input type="range" id="chunk-steps" min="1" max="50" value="10"></label>
<label for="latency-ms">Model gecikmesi (ms)<input type="range" id="latency-ms" min="10" max="1500" step="10" value="150"></label>
</div>
<div class="lab-result" id="chunk-result" aria-live="polite"></div>
</div>

**Deney:** 30 Hz'de 50 eylem yaklaşık 1,67 saniyelik pencere demektir. O sürede nesne kayarsa eski tahminler hâlâ yürütülüyor olabilir. Daha kısa pencere daha sık geri besleme isteyebilir; inference bunu yetiştiremiyorsa eylem kuyruğu boşalabilir. Bu hesap gerçek bir RTC uygulaması değildir; gecikme bütçesini anlamaya yarar.

<noscript>İnteraktif hesaplar için JavaScript gerekir. Formüller ve açıklamalar sayfada okunabilir; aynı konuları Python örnekleriyle çalışabilirsin.</noscript>
