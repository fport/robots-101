# Kaynaklar ve sürümler

Kontrol tarihi: **8 Eylül 2026**. Bu sayfalar Türkçe bir çalışma rehberi olarak özgün açıklamalar ve örnek deneylerle hazırlandı. Aşağıdaki birincil kaynaklar API/ürün/model bilgilerinin dayanağıdır; üçüncü tarafların bütün dokümanları burada yeniden yayımlanmıyor.

## Senin verdiğin kaynaklar

| Kaynak | Bu rehberde kullanımı |
|---|---|
| [strands-labs/robots](https://github.com/strands-labs/robots) | Ana sim/robot entegrasyonu; kaynak kodu ve yayımlanmış paket incelendi |
| [Hashtag Robotics SO-101](https://labs.hashtagrobotics.tr/so-101-robot-kol) | Kit bağlamı, leader/follower, bileşen ve eklenti bilgisi |
| [Qwak CDN HashtagRobotics adresi](https://cdn-avatars.qwak.ai/HashtagRobotics) | Tarayıcı aracıyla okunabilir içerik alınamadı; teknik bilgi kaynağı olarak kullanılmadı |

CDN adresinin bir eğitim kılavuzu, marka varlığı veya başka bir kaynak olduğunu erişim başarısızlığından çıkarmadık. Ürün iddialarıyla bağımsız test sonuçlarını birbirine karıştırmadık.

## Ana teknik kaynaklar

| Konu | Kaynak |
|---|---|
| Robot tasarımı ve modeller | [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) |
| SO-101 kurulum | [LeRobot SO-101](https://huggingface.co/docs/lerobot/en/so101) |
| LeRobot kurulumu | [Installation](https://huggingface.co/docs/lerobot/en/installation) |
| Teleop/kayıt/eğitim | [Imitation learning](https://huggingface.co/docs/lerobot/en/il_robots) |
| Kameralar | [Camera guide](https://huggingface.co/docs/lerobot/en/cameras) |
| Kamera matematiği | [OpenCV kalibrasyon öğreticisi](https://docs.opencv.org/4.13.0/dc/dbb/tutorial_py_calibration.html), [calib3d API](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html) |
| Sayısal ters kinematik | [Lynch/Park, Modern Robotics 6.2](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-1-of-2/) |
| Optimizer | [PyTorch AdamW](https://docs.pytorch.org/docs/stable/generated/torch.optim.AdamW.html) |
| Dataset v3 | [LeRobotDataset v3](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3) |
| SmolVLA | [Policy docs](https://huggingface.co/docs/lerobot/en/smolvla), [makale](https://arxiv.org/abs/2506.01844), [model](https://huggingface.co/lerobot/smolvla_base) |
| Kamera eşleme | [Rename map](https://huggingface.co/docs/lerobot/en/rename_map) |
| ACT | [ACT docs](https://huggingface.co/docs/lerobot/en/act) |
| Donanımda inference | [Rollout](https://huggingface.co/docs/lerobot/en/inference) |
| Asenkron/RTC | [Async](https://huggingface.co/docs/lerobot/en/async), [RTC](https://huggingface.co/docs/lerobot/en/rtc) |
| MuJoCo genel bakış | [Overview](https://mujoco.readthedocs.io/en/stable/overview.html) |
| MuJoCo Python | [Python bindings](https://mujoco.readthedocs.io/en/stable/python.html) |
| MuJoCo modelleme | [Modeling](https://mujoco.readthedocs.io/en/stable/modeling.html), [XML reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html) |
| Strands sim | [Simulation overview](https://strands-labs.github.io/robots/simulation/overview/) |
| Strands kayıt | [Recording](https://github.com/strands-labs/robots/blob/main/docs/recording.md) |
| Strands policy | [LeRobot local](https://github.com/strands-labs/robots/blob/main/docs/policies/lerobot-local.md) |
| Strands eğitim | [Training overview](https://github.com/strands-labs/robots/blob/main/docs/training/overview.md) |
| Python ortamı | [uv](https://docs.astral.sh/uv/) |
| Site | [MkDocs](https://www.mkdocs.org/), [Material](https://squidfunk.github.io/mkdocs-material/) |

## Sürüm sabitleme

| Bileşen | Bu atölyenin tabanı |
|---|---|
| Python | 3.12.12, macOS arm64 üzerinde |
| MkDocs | 1.6.1 |
| Material | 9.7.7 |
| Strands Robots | 0.5.1 |
| MuJoCo | 3.12.0 |
| LeRobot | 0.6.1 |
| PyTorch / torchvision / torchcodec | ML ortamının `constraints-ml-macos.txt` dökümünde |

`requirements-docs.txt`, `requirements-sim.txt`, `requirements-ml.txt` ana paketleri sabitler. `constraints-*.txt` bu Mac'teki transitive paketlerin tam referansıdır; Linux/CUDA için körlemesine aynı wheel/platform seçimi kabul edilmez. Yeni ortamı çözdükten sonra kendi `uv pip freeze` çıktını kaydet.

İncelenen GitHub kaynak commit'leri:

- Strands Robots: [`82be6e684314c20a2778c4927f63f2d737795b43`](https://github.com/strands-labs/robots/tree/82be6e684314c20a2778c4927f63f2d737795b43)
- LeRobot: [`2774d9bddcbbda50e697e162e89e7eaada8d7105`](https://github.com/huggingface/lerobot/tree/2774d9bddcbbda50e697e162e89e7eaada8d7105)
- `robot_descriptions` tarafından indirilen SO-ARM100 modeli: `63eede5a636e548eb8f2854e558bd343c21db9f7`

GitHub LeRobot kaynağı 0.6.2 geliştirme sürümünü işaret ediyordu; PyPI'da bu sürüm bulunmadığı için çalıştırmalar **0.6.1** ile yapıldı. GitHub'daki yenilikleri kurulu pakette varmış gibi kullanmamak için komut yardım çıktıları ve kurulu kaynak da incelendi.

## Güncelleme yöntemi

Çalışan ortamı koru. Yeni paketleri ayrı `.venv-next` ortamında dene; önce physics, sonra SO-101 render, dataset kaydı/okuma, şema denetimi ve kısa eğitim. Başarılıysa sürüm dosyalarını ve doğrulama sayfasını birlikte güncelle.

Model ağırlıklarını indirirken model repo revision'ını ayrıca kaydet. Python paketini sabitlemek Hub'daki `main` ağırlığını sabitlemez. Dataset, base model ve kendi checkpoint'inin kaynaklarını deney defterinde ayrı satırlarda tut.
