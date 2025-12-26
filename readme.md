# CPU vs GPU: Pixel Rendering Simulation

Bu proje, bilgisayar mimarisi derslerinde veya teknik sunumlarda **Merkezi İşlem Birimi (CPU)** ile **Grafik İşlem Birimi (GPU)** arasındaki çalışma mantığı farkını görselleştirmek için tasarlanmıştır.

## 🎯 Projenin Amacı
Sözel olarak anlatılması zor olan "Seri İşlem" (Serial) ve "Paralel İşlem" (Parallel) kavramlarını, bir resmin piksellerinin oluşturulma süreci üzerinden **canlı bir simülasyonla** göstermektir.

* **CPU Modu:** Tek bir işçinin (Thread) resmi piksel piksel, sırayla boyamasını simüle eder.
* **GPU Modu:** Yüzlerce işçinin (Cuda Cores) resmin rastgele bölgelerine aynı anda saldırarak resmi oluşturmasını simüle eder.

## 🛠 Gereksinimler

Bu uygulama **Windows, macOS (Intel & M1/M2) ve Linux** işletim sistemlerinde çalışır. Özel bir ekran kartı sürücüsüne (CUDA vb.) ihtiyaç duymaz, çünkü mantıksal simülasyon yapar.

Aşağıdaki yazılımların yüklü olması gerekir:

* **Python 3.x**
* **Kütüphaneler:**
    * `pygame` (Arayüz ve grafikler için)
    * `numpy` (Matris işlemleri için)

## 🚀 Kurulum

1.  Python yüklü değilse [python.org](https://www.python.org/) adresinden indirin.
2.  Terminal veya Komut İstemi'ni (CMD) açın.
3.  Gerekli kütüphaneleri yüklemek için şu komutu yazın:

```bash
pip install pygame numpy
```

4.  Proje klasörünün içine işlem yapılacak resmi **`resim.jpg`** adıyla kaydedin. (Önerilen boyut: 800x600 veya civarı).

## ▶️ Kullanım

Uygulamayı başlatmak için terminalden şu komutu çalıştırın:

```bash
python main.py
```

### Arayüz Kontrolleri
* **Mouse:** Menüdeki butonları seçmek için mouse kullanabilirsiniz.
* **CPU BAŞLAT:** Seri işlem modunu açar (Yeşil Tekli İmleç).
* **GPU BAŞLAT:** Paralel işlem modunu açar (Mavi Çoklu İmleç).
* **GERİ DÖN:** Simülasyon sırasında sol üstteki butona basarak ana menüye dönebilirsiniz.
* **ESC:** Uygulamadan tamamen çıkış yapar.

## ⚙️ Özelleştirme (Opsiyonel)

`main.py` dosyasını bir metin editörüyle açarak simülasyon hızlarını sunumunuza göre ayarlayabilirsiniz:

```python
# SİMÜLASYON AYARLARI
CPU_ADIM = 30        # CPU'nun hızını artırmak için bu sayıyı yükseltin
GPU_PARALEL = 400    # GPU'nun aynı anda kaç piksel boyayacağını belirler
```

## 📝 Sunum Notları

İzleyicilere gösterirken şunlara dikkat çekin:

1.  **CPU Modunda:** İmlecin sol üstten başlayıp daktilo gibi satır satır gittiğini vurgulayın. "CPU zekidir ama tek tek iş yapar."
2.  **GPU Modunda:** Resmin bir anda her yerden belirdiğini vurgulayın. "GPU'nun binlerce küçük eli vardır, hepsi aynı anda çalışır."

---
*Hazırlayan: [Senin Adın]*