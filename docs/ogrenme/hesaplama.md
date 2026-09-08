# GPU ve bulut çalışma düzeni

Robotun yanında Mac kullanıp eğitimi başka bilgisayarda yapabilirsin. Veri toplama makinesi ile eğitim (training) makinesini ayırmak robotun sürekli ağa bağlı kontrol edilmesini gerektirmez; eğitimden sonra kontrol noktası (checkpoint)'i geri getirirsin.

## İşleri bilgisayarlara dağıt

| İş | Mac/CPU | NVIDIA CUDA makinesi |
|---|---|---|
| MkDocs, küçük Python alıştırmaları | Uygun başlangıç | Gerekmez |
| Tek SO-101 MuJoCo fizik sim | Çalıştırıldı | Yapılabilir |
| Kamera/veri kaydı | USB/codec uyumuna bağlı | Yapılabilir |
| Küçük NumPy taklit öğrenme (imitation learning) | Çalıştırılabilir | Gerekmez |
| SmolVLA ince ayar (fine-tuning) | CPU yavaş; MPS ayrıca sınanmalı | Ana eğitim tarifi |
| Gerçek zamanlı VLA | Gecikme (latency)/bellek ölçülmeli | Cihaz/model/ayarına bağlı |

Kesin VRAM gereksinimi sabit değildir: örnek grubu (batch), görüntü sayısı/boyutu, hassasiyet, eğitilen katmanlar ve eniyileyici (optimizer) etkiler. Önce batch 1 ile bellek ölç; sonra artır. “450M parametre” toplam eğitim belleğini hesaplamak için tek başına yeterli değildir. [LeRobot hesaplama rehberi](https://huggingface.co/docs/lerobot/en/hardware_guide)

## CUDA kurulum sırası

Linux makinede NVIDIA sürücüsünü sağlayıcının/dağıtımın talimatıyla kur. `nvidia-smi` sürücüyü görmeli. PyTorch'un desteklediği CUDA wheel'ini [resmî PyTorch kurulum seçicisinden](https://pytorch.org/get-started/locally/) belirle; rastgele CUDA index URL'si kullanma.

```bash
uv venv --python 3.12 .venv-ml
uv pip install --python .venv-ml/bin/python -r requirements-ml.txt
source .venv-ml/bin/activate
python examples/00_doctor.py
python -c 'import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CUDA yok")'
```

`cuda.is_available()` false ise eğitimi başlatmadan önce sürücü/wheel/görünür cihaz sorununu çöz. Bir container içinde GPU'nun host'ta görünmesi container'a aktarıldığı anlamına gelmez. Mac'te CUDA yoktur; `device=cuda` yerine MPS/CPU seçimi gerekir.

## Video bağımlılıkları

TorchCodec, PyTorch sürümü ve shared FFmpeg kütüphaneleriyle uyumlu olmalıdır. Sistemde bir `ffmpeg` çalıştırılabilir dosyası bulunması, `libavutil` gibi dinamik kütüphanelerin loader tarafından bulunacağını garanti etmez. [TorchCodec kurulum ve uyumluluk tablosu](https://github.com/pytorch/torchcodec#installing-torchcodec)

Bu Mac'te sistem FFmpeg bulunmadığı için TorchCodec yüklenemedi; LeRobot PyAV'a geri düştü. Veri kaydı ve PyAV ile okuma sınandı. Daha sonra TorchCodec kullanmak istersen uygun FFmpeg'i sistem paket yöneticisiyle kur, kütüphane yolunu resmî açıklamaya göre kontrol et ve küçük bir video decode testi çalıştır. Eğitim tarifimiz PyAV'ı açık seçtiği için bu ayrı kurulum ilk denemeyi engellemez.

## Yerel veriyi eğitim sunucusuna taşı

1. Robot makinesinde kaydı sonlandır ve veri kümesi (dataset) denetimini çalıştır.
2. Veri kökünü `meta`, `data`, `videos` birlikte olacak şekilde paketle/aktar.
3. Eğitim makinesinde aynı denetimi ve bir kare (frame) okuma deneyini çalıştır.
4. Eğitim komutunu o makinedeki yollarla yeniden üret.
5. Sonuçta checkpoint, komut, sürüm dökümü ve değerlendirme notlarını geri al.

Örnek SSH aktarımı; host/yolları kendi sunucuna göre değiştir:

```bash
rsync -av --progress data/so101-pick-v1/ USER@GPU_HOST:/workspace/data/so101-pick-v1/
```

Bu komut bir GPU sunucusu oluşturmaz. Elinde mevcut sunucu veya açtığın bir bulut oturumu olmalı. SSH kimlik bilgilerini repo dosyalarına yazma.

## Bulut kullanırken deney bütçesi

İlk oturumda bütün büyük eğitimi başlatma. Ortam, veri okuma ve 100 adımlık deneme bitsin. Kararlı adım süresi ölçüldükten sonra kalan süreyi yaklaşık hesapla:

```text
tahmini eğitim süresi ≈ kalan adım × kararlı saniye/adım
toplam süre ≈ kurulum + indirme + eğitim + değerlendirme + checkpoint aktarımı
```

Maliyet seçtiğin sağlayıcının güncel saatlik bedeli, storage ve ağ politikasına bağlıdır; burada sabit fiyat verilmez. Notebook arayüzünü kapatmak GPU instance'ını durdurmayabilir. Sağlayıcı panelinden iş/instance durumunu kontrol et ve checkpoint'leri kalıcı diske taşı.

Kesilebilir GPU oturumunda checkpoint sıklığını kaybedebileceğin süreye göre belirle. Her adımda checkpoint yazmak gereksiz I/O olabilir; hiç yazmamak kesintide bütün koşuyu kaybettirebilir. Resume işlemini uzun işe güvenmeden önce küçük bir koşuda dene.

## Birden fazla GPU ne zaman?

Önce tek GPU'da çalışan, anlamlı veriyle doğrulanmış bir eğitim hattı kur. Multi-GPU'nun communication, effective batch ve reproducibility etkileri vardır. Bu proje tek GPU komutunu verir; dağıtılmış eğitim ayrı optimizasyon ödevidir. [LeRobot çoklu GPU rehberi](https://huggingface.co/docs/lerobot/en/multi_gpu_training)
