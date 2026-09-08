# Sözlük

| Terim | Anlamı |
|---|---|
| Eylem (Action) | Kontrol döngüsünde gönderilen hedef/komut; semantiği robot/policy belirler |
| Eylem dizisi (Action chunk) | Geleceğe ait bir eylem dizisi |
| ACT | Action Chunking with Transformers; taklit öğrenme politikası |
| Aktüatör (Actuator) | Simde veya robotta hareket üreten sürücü/motor mekanizması |
| Model varlığı (Asset) | Mesh, MJCF ve ilişkili model dosyaları |
| Davranış kopyalama (BC) | Behavior cloning; uzman gözlem/eylem eşlemesini öğrenme |
| Kalibrasyon (Calibration) | Ölçüm/hedef değerlerini robotun referanslarıyla ilişkilendirme |
| Kontrol noktası (Checkpoint) | Ağırlıklar ve ilgili çalışma/eğitim durumunu içeren kayıt |
| Kontrol frekansı (Control frequency) | Yeni kontrol eylemlerinin yürütülme sıklığı |
| CUDA | NVIDIA GPU üzerinde kullanılan hesaplama altyapısı |
| Veri kümesi (Dataset) | Zamanla ilişkili gözlem, eylem, görev ve metadata kayıtları |
| Göreli eylem (Delta action) | Mevcut referansa göre değişim komutu |
| Serbestlik derecesi (DOF) | Serbestlik derecesi |
| Ortam çeşitlendirmesi (Domain randomization) | Eğitim ortamındaki görsel/fiziksel değişkenleri kontrollü çeşitlendirme |
| Robotun gövde/sensör/eylem yapısı (Embodiment) | Robotun gövdesi, sensörleri ve eylem/durum temsilinin bütünü |
| Uç işlevci (End effector) | Kolun iş yapan ucu; burada tutucu |
| Bölüm / görev denemesi (Episode) | Başlangıcı ve sonu tanımlı bir görev denemesi |
| Veri üzerinden geçiş (Epoch) | Eğitim verisinin yaklaşık bir kez tüketilmesine karşılık gelen ölçü |
| İleri kinematik (FK) | İleri kinematik; eklemlerden uç pozuna |
| Takipçi kol (Follower) | Görevi fiziksel olarak yapan robot kol |
| Kare / zaman örneği (Frame) | Bir zaman örneği; bağlama göre görüntü veya bütün gözlem |
| Tutucu (Gripper) | Nesneyi kavrayan tutucu |
| Penceresiz çalışma (Headless) | Etkileşimli pencere olmadan çalışma; render bağımlılığı yine olabilir |
| İnsanın döngüye katılması (HIL) | Human in the loop; insanın düzeltme/değerlendirme döngüsüne katılması |
| Ters kinematik (IK) | Ters kinematik; uç hedefinden eklem değerlerine |
| Taklit öğrenme (Imitation learning) | Gösterimlerden davranış öğrenme |
| Çıkarım (Inference) | Öğrenilmiş ağırlıklarla yeni eylem tahmini |
| Eklem (Joint) | Hareket serbestliği sağlayan eklem |
| Önder kontrol kolu (Leader) | İnsan hareketini komuta dönüştüren kontrol kolu |
| Düşük dereceli uyarlama (LoRA) | Düşük rank adaptörlerle parametre verimli uyarlama yöntemi |
| Kayıp (Loss) | Eğitim tahminiyle hedef/öğrenme amacı arasındaki sayısal kayıp |
| Üstveri (Metadata) | Verinin şeması, sayıları, zamanları, görev ve dosya bilgileri |
| MJCF | MuJoCo'nun XML model tanım biçimi |
| MPS | Apple GPU için PyTorch hesaplama yolu |
| MuJoCo | Eklemli cisim ve temas dinamiği fizik motoru |
| Normalizasyon (Normalization) | Özelliklerin istatistik/ölçek dönüşümü |
| Gözlem (Observation) | Karar anındaki görüntü, durum ve diğer sensör girdileri |
| Aşırı uyum (Overfitting) | Eğitim örneklerine uyup yeni koşullara iyi genelleyememe |
| Parquet | Sütun temelli tablo dosyası biçimi |
| Politika (Policy) | Gözlem/görevden eylem üreten davranış modeli veya denetleyici |
| Ön eğitim (Pretraining) | Göreve özgü uyarlama öncesi geniş kapsamlı öğrenme |
| Öz durum algısı (Proprioception) | Robotun kendi eklem/durum ölçümleri |
| qpos / qvel | MuJoCo genel konum ve hız durumları |
| Pekiştirmeli öğrenme (RL) | Reinforcement learning; ödül üzerinden etkileşimle öğrenme |
| Politika yürütümü (Rollout) | Bir politikanın ortamda zaman boyunca yürütülmesi |
| Gerçek zamanlı eylem dizileme (RTC) | Real-time chunking; eylem dizilerinin zamanlama/geçiş yönetimi |
| Rastgelelik tohumu (Seed) | Rastlantısal sürecin başlangıç değeri; tek başına tam yeniden üretim garantisi değil |
| Simülasyondan gerçeğe aktarım (Sim2real) | Simülasyonda öğrenilen/kurulan davranışı gerçek sisteme taşıma |
| SmolVLA | LeRobot ekosistemindeki kompakt vision-language-action modeli |
| Durum (State) | Robotun o anki ölçülen durum vektörü |
| Teleoperasyon (Teleoperation) | Bir insan/kontrolcünün robotu uzaktan yönlendirmesi |
| Fizik zaman adımı (Timestep) | Fizik motorunun bir adımda ilerlettiği sim zamanı |
| URDF | Robot geometrisi/eklem yapısı için yaygın XML tanımı |
| Doğrulama (Validation) | Model/ayar seçiminde kullanılan ayrılmış veri değerlendirmesi |
| Görüntü–dil–eylem (VLA) | Vision–Language–Action; görüntü, dil ve eylemi bağlayan politika |
| GPU belleği (VRAM) | GPU belleği |
| Ara hedef (Waypoint) | Hareketin geçmesi istenen ara hedef |

## Öğrenme döngüsünde karşılaşacağın ek terimler

| Terim | Anlamı |
|---|---|
| Örnek grubu (batch) | Bir eğitim güncellemesinde birlikte işlenen örnekler |
| İnce ayar (fine-tuning) | Hazır model ağırlıklarını kendi görevine uyarlama |
| Öğrenme oranı (learning rate) | Parametre güncellemesinin ölçeğini etkileyen ayar |
| Eniyileyici (optimizer) | Gradyanları kullanarak ağırlıkları güncelleyen algoritma |
| Gradyan (gradient) | Parametre değişince kaybın nasıl değiştiğini gösteren türev |
| Tensör (tensor) | Çok boyutlu sayısal dizi |
| Doldurma (padding) | Şekli sabit tutan ek değerler; gerçek etiket olmayanlar maskelenir |
| Gösterim (demonstration) | Öğretmenin görevi nasıl yaptığını gösteren kayıt |
| Bağlantı (link) | Eklemler arasındaki rijit kol parçası |
| Sürtünme (friction) | Temasta göreli kaymaya karşı etki |
| Sıfırlama (reset) | Yeni deneme için tanımlı başlangıç durumuna dönme |
| Sürüm (revision) | Bir veri veya model deposunun belirli kayıt kimliği |
| Akış eşleme (flow matching) | Gürültü ve veri arasında koşullu yön/hız alanı öğrenme |

Bir terimi öğrendiğinde birim, referans, sıra ve zaman sözleşmesini de sor. “Eylem” sözcüğünü bilmek altı sayının robota ne yaptırdığını tek başına açıklamaz.
