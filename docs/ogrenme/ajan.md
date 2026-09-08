# Strands ajanı ile birleştirme

Robot önce doğrudan Python ile kontrol edilebilir olmalı. Sonra dil modeli, “sahne oluştur”, “kamera görüntüsü al”, “bu kayıtlı politikayı kısa süre çalıştır” gibi üst düzey görevleri araç çağrılarıyla yönetebilir.

## Aynı araç, iki kullanım biçimi

```python
from strands_robots import Robot

sim = Robot("so101", mode="sim", mesh=False)
print(sim.get_robot_state("so101"))
sim.cleanup()
```

Bu doğrudan API yoludur. LLM sağlayıcısı ayarlandığında aynı sim nesnesi bir Strands Agent'a araç olarak verilebilir:

```python
# Sağlayıcı hesabı/model erişimi önceden kurulmuş olmalı.
from strands import Agent
from strands_robots import Robot

sim = Robot("so101", mode="sim", mesh=False)
try:
    agent = Agent(tools=[sim])
    agent("Mevcut so101 robotunun durumunu oku ve açıkla. Dünyayı yeniden oluşturma.")
finally:
    sim.cleanup()
```

Parametresiz `Agent` varsayılan olarak Amazon Bedrock sağlayıcısını kullanır; bu yolu seçeceksen AWS kimlik bilgileri ve model erişimi gerekir. Bu örnek sağlayıcının varsayılan model ayarını kullanır; hesabın/kimlik bilgilerin yoksa çalışması beklenmez. Model seçimi ve kimlik doğrulama [Strands model provider belgelerinden](https://strandsagents.com/docs/user-guide/concepts/model-providers/) yapılır. İlk sim laboratuvarları bu adıma bağlı değildir.

## Ajan ile VLA aynı model değildir

Strands Agent, talebi parçalayıp araç seçer. SmolVLA, anlık görüntü/durum/görevden motor eylemleri üretir. Bir ajan “pick” aracını seçebilir; alttaki politika hareket döngüsünü yürütür. Her 30 Hz motor komutunu ayrı sohbet isteği yapmak gecikme ve tutarlılık sorunları yaratabilir.

## Deterministik işler kodda kalsın

Episode sayımı, dosya sonlandırma, hata denetimi ve ölçüm kaydı Python döngüsünde açık biçimde yapılmalı. “20 gösterim topladım” şeklinde dil modeli anlatımı gerçek metadata'nın yerine geçmez. `03_record_sim.py` bu yüzden her episode'u kodla kaydeder ve gerçek sayıyı doğrular.

## Önerilen ilk ajan görevleri

| İstek | Beklenen denetlenebilir sonuç |
|---|---|
| “Robotun eklemlerini listele.” | State API çıktısı |
| “Mevcut kameraları göster.” | Kamera adları |
| “Front kameradan görüntü al.” | Render görüntüsü |
| “Bu rapordaki hataları açıkla.” | Önceden üretilmiş metriklere dayanan yorum |

Ajanın bir görsele bakıp “başarılı kavrama” demesi, fiziksel başarı ölçütünü otomatik doğrulamaz. Görsel değerlendirme yardımcı bir sinyal olabilir; nesnenin kapta kalması gibi ölçümleri ayrı koru.

## Donanıma geçince

Önce LeRobot ile çalıştığı doğrulanan kalibrasyon, kamera, birim ve kısa rollout kullanılır. Strands hardware kurulumunda aynı parametrelerin/processor'ların taşındığını kontrol et. Donanımı birden fazla süreç yönetmesin. İlk agent görevi motor hareketi istemek yerine durum okumak olabilir.

İleri tasarımda ajan yalnız önceden tanımlı görevleri başlatır; hareket süresi, eylem limitleri, timeout ve hata dönüşü uygulama katmanında belirlenir. Bu, robot görevinin somut çalışma sözleşmesidir. [Strands Robots API](https://github.com/strands-labs/robots/blob/main/docs/api-reference.md)
