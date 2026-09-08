# Strands ile SO-101

Bu bölüm senin verdiğin [strands-labs/robots](https://github.com/strands-labs/robots) projesini doğrudan kullanır. Rehberin çalıştırılan paketi `strands-robots==0.5.1`. GitHub `main` dokümanında görebileceğin her yeni parametrenin bu sürümde bulunduğunu varsayma.

## İlk programın anatomisi

Tam çalışan dosya: `examples/02_strands_so101.py`.

```python
from strands_robots import Robot

sim = Robot("so101", mode="sim", mesh=False)
try:
    result = sim.get_robot_state("so101")
    print(result)
finally:
    sim.cleanup()
```

`Robot` fabrika fonksiyonudur. Bu çağrı hazır dünya/robot döndürür; üzerine tekrar `create_world()` çağırma. Daha alt seviyede `Simulation()` ile başladığında dünyayı ve robotu sen eklersin. İki başlangıç biçimini birbiriyle karıştırma.

`mode="sim"` açıkça simülasyonu seçer. `mesh=False` bu alıştırmada filo ağını kapatır. Gerçek donanım başka bir bölümde `mode="real"` ve seri port ile ele alınır.

## Çalıştır

```bash
.venv/bin/python examples/02_strands_so101.py --render --steps 30
```

Program SO-101'i yükler, küçük bir küp ve `front` kamera ekler, başlangıç state'ini okur, mock politika ile 30 kontrol adımı çalıştırır ve iki görüntü kaydeder. `outputs/so101_before.png` başlangıç, `outputs/so101_after.png` son durumdur.

Masaüstünde hareketi canlı izlemek için macOS'ta aşağıdaki komutu kullan. 900 kontrol adımı yaklaşık 30 saniyelik izleme penceresi verir; çıkışta pencere temizlenir. Linux masaüstünde `mjpython` yerine `python` kullanılır.

```bash
.venv/bin/mjpython examples/02_strands_so101.py --viewer --steps 900
```

Bu gerçek MuJoCo görüntüleyicisidir: kamerayı fareyle değiştirip robotu farklı açılardan inceleyebilirsin. Hareket kaynağı yine mock politikadır. `Ctrl+C` scripti bitirir; pencereli kullanım yerel ekran oturumu gerektirir.

![Bu projede MuJoCo ile üretilmiş SO-101 başlangıç sahnesi](../assets/so101-sim.png)

*Bu ekran görüntüsü `02_strands_so101.py` çalıştırılarak üretildi. Model varlığı: [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100); yükleyici: Strands Robots / robot_descriptions. Hashtag Robotics kitinin birebir malzeme ve dinamik kalibrasyonu değildir.*

## Dönen sonucu doğru oku

Araçlar çoğunlukla `status` ve `content` taşıyan sözlük döndürür. Python çağrısının exception atmaması işlemin başarılı olduğunu tek başına göstermez. Örneklerdeki `checked(...)`, `status="error"` sonucunu da hata hâline getirir.

```python
result = sim.get_robot_state("so101")
if result["status"] != "success":
    raise RuntimeError(result)
```

İnsan için açıklama `content` içindeki `text`, makinece işlenecek alanlar `json` bloklarında olabilir. `get_robot_state` çıktısındaki eklem isimlerini not et. Test edilen SO-101 modelinde `1`–`6` adları döndü; gerçek LeRobot donanımında isimlerin aynı olduğunu varsayma.

## Mock ne işe yarar?

Mock politika arayüzün eylem üretip simülatöre aktarabildiğini sınar. Aşağıdaki sonuçları gösterebilir: model yüklendi, politika çağrıldı, eylem anahtarları çözüldü, fizik adımlandı, görüntü üretildi.

Şunları göstermez: küp tanındı, kavrama planlandı, tutucu temas kurdu veya bir görev öğrenildi. `instruction="pick up the cube"` yazmak mock'u kavrama uzmanına dönüştürmez. `status="success"` çoğu kez API işleminin tamamlandığı anlamına gelir; görev başarısının ayrı ölçütü olmalıdır.

## Kendin değiştir

1. Küpün rengini turuncudan maviye çevir. Görüntü değişmeli; mock davranışın bu rengi anlayarak değişmesini bekleme.
2. Kamerayı diğer yana taşı. Görsel algı modelinin girdisinin ne kadar değiştiğini düşün.
3. `--steps 60` çalıştır. Robot state ve sim zamanı değişimini oku.
4. Sadece `sim.render()` çağır; bunun robotu ileri adımlamadığını gözle.

İlk model indirmesi tamamlandıktan sonra aynı önbellekle model yüklemek genellikle internet gerektirmez. Scriptler proje altındaki `.cache/` dizinlerini kullanır; robot varlıkları ve daha sonra indirilecek VLA ağırlıkları ayrı şeylerdir.

Kaynak/API ayrıntısı: [Strands simulation overview](https://strands-labs.github.io/robots/simulation/overview/).
