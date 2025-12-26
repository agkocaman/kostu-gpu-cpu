import pygame
import torch
import numpy as np
import time
import sys

# --- AYARLAR ---
GENISLIK, YUKSEKLIK = 1000, 700  # Ekranı biraz büyüttük (Dashboard için yer)
RESIM_ADI = "resim.jpg"         # Yanına güzel, yüksek çözünürlüklü bir resim koy
GPU_SHOW_SURESI = 10.0          # GPU şovu kaç saniye sürsün?

# Renkler
RENK_ARKA = (30, 30, 35)
RENK_BAR_BOS = (50, 50, 50)
RENK_CPU_BAR = (255, 100, 100) # Kırmızı
RENK_GPU_BAR = (100, 255, 100) # Yeşil
RENK_YAZI = (220, 220, 220)

# Pygame Başlatma
pygame.init()
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("PROJE: CPU vs GPU Görüntü İşleme Benchmark")

# Fontlar
font_baslik = pygame.font.SysFont('Consolas', 32, bold=True)
font_bilgi = pygame.font.SysFont('Consolas', 18)
font_dev = pygame.font.SysFont('Arial', 60, bold=True)

# Resmi Yükle
try:
    ham_resim = pygame.image.load(RESIM_ADI)
    # Resmi ekrana sığacak ama altta boşluk kalacak şekilde ayarla (Dashboard için)
    resim_alani = (GENISLIK, YUKSEKLIK - 100) 
    orijinal_resim = pygame.transform.scale(ham_resim, resim_alani)
except FileNotFoundError:
    print(f"HATA: '{RESIM_ADI}' dosyası bulunamadı!")
    pygame.quit()
    sys.exit()

resim_array = pygame.surfarray.array3d(orijinal_resim) # (W, H, 3)

# --- YARDIMCI FONKSİYONLAR ---

def dashboard_ciz(mod, yuzde, fps=0, extra_text=""):
    """Ekranın altına istatistik ve progress bar çizer"""
    # Alt panel arka planı
    pygame.draw.rect(ekran, (20, 20, 20), (0, YUKSEKLIK-100, GENISLIK, 100))
    
    # Progress Bar Arka Plan
    bar_rect = (50, YUKSEKLIK-40, GENISLIK-100, 20)
    pygame.draw.rect(ekran, RENK_BAR_BOS, bar_rect)
    
    # Progress Bar Doluluk
    doluluk = int((GENISLIK-100) * (yuzde / 100))
    renk = RENK_GPU_BAR if "GPU" in mod else RENK_CPU_BAR
    pygame.draw.rect(ekran, renk, (50, YUKSEKLIK-40, doluluk, 20))
    
    # Yazılar
    yazi_mod = font_baslik.render(f"MOD: {mod}", True, renk)
    yazi_fps = font_bilgi.render(f"PERFORMANS: {fps:.1f} FPS" if fps > 0 else "HESAPLANIYOR...", True, RENK_YAZI)
    yazi_extra = font_bilgi.render(extra_text, True, (150, 150, 150))
    
    ekran.blit(yazi_mod, (50, YUKSEKLIK-85))
    ekran.blit(yazi_fps, (350, YUKSEKLIK-80))
    ekran.blit(yazi_extra, (GENISLIK-300, YUKSEKLIK-80))
    
    # Çerçeve
    pygame.draw.rect(ekran, (100,100,100), (0, YUKSEKLIK-100, GENISLIK, 100), 1)

def sepia_filtresi_cpu_show(img_array):
    """CPU: Görsel şov için yavaşlatılmış ve görselleştirilmiş işlem"""
    w, h, c = img_array.shape
    yeni_resim = np.zeros_like(img_array)
    
    # Orijinal resmi önce bir gösterelim (grileşmiş gibi)
    ekran.blit(pygame.surfarray.make_surface(img_array), (0,0))
    pygame.display.flip()
    
    baslangic = time.time()
    
    # Tarama efekti için döngü
    adim = 10 # Her seferde 10 sütun işle (Performans/Görsel denge)
    
    for x in range(0, w, adim):
        # Olayları dinle (Pencere donmasın diye)
        pygame.event.pump()
        
        # Bu sütun bloğunu işle
        limit_x = min(x + adim, w)
        for i in range(x, limit_x):
            for j in range(h):
                r, g, b = img_array[i, j]
                # Basit Sepia
                tr = min(255, int(0.393*r + 0.769*g + 0.189*b))
                tg = min(255, int(0.349*r + 0.686*g + 0.168*b))
                tb = min(255, int(0.272*r + 0.534*g + 0.131*b))
                yeni_resim[i, j] = [tr, tg, tb]
        
        # Görselleştirme (Parça parça çiz)
        if x % 20 == 0: # Çok sık çizip daha da yavaşlatmayalım
            # İşlenmiş kısmı alıp ekrana basmak yerine, sadece o şeridi blit edebiliriz ama
            # Pygame array handling biraz tricky, tüm resmi basmak daha güvenli:
            surf = pygame.surfarray.make_surface(yeni_resim)
            ekran.blit(surf, (0,0))
            
            # Tarama Çizgisi (Lazer gibi)
            pygame.draw.line(ekran, (255, 50, 50), (x, 0), (x, YUKSEKLIK-100), 3)
            
            # Dashboard Güncelle
            yuzde = (x / w) * 100
            gecen_sure = time.time() - baslangic
            dashboard_ciz("CPU (Single Core)", yuzde, 0, f"Süre: {gecen_sure:.1f}sn")
            
            pygame.display.flip()
            
            # CPU'yu sunumda göstermek için bilerek minicik bekletme (Opsiyonel)
            # time.sleep(0.001) 

    bitis = time.time()
    return yeni_resim, bitis - baslangic

def gpu_show_loop(tensor_img):
    """GPU: Tek kare değil, sürekli akan bir video render simülasyonu"""
    device = tensor_img.device
    w, h, c = tensor_img.shape
    
    # Başlangıç zamanı
    baslangic = time.time()
    frame_count = 0
    
    # Sepia Temel Matrisi
    base_matrix = torch.tensor([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ], device=device).t()

    running_gpu = True
    while running_gpu:
        current_time = time.time()
        gecen = current_time - baslangic
        
        # Süre dolduysa çık
        if gecen > GPU_SHOW_SURESI:
            break
            
        # Olayları kontrol et (Çıkış için)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # --- DİNAMİK EFEKT ---
        # Matrisi zamanla hafifçe değiştirerek "Video Oynatıyor" hissi verelim
        # Sinüs dalgası ile renk yoğunluğunu değiştiriyoruz
        degisim = np.sin(gecen * 2) * 0.1 
        matrix = base_matrix + degisim
        
        # GPU İŞLEMİ (Heavy Lifting)
        img_float = tensor_img.float()
        sonuc = torch.matmul(img_float, matrix)
        sonuc = torch.clamp(sonuc, 0, 255).byte()
        
        if device == "mps" or device == "cuda":
            torch.mps.synchronize() if device == "mps" else torch.cuda.synchronize()
        
        # Ekrana Bas (GPU'dan CPU'ya veri çekmek darboğazdır ama şov için mecburuz)
        sonuc_np = sonuc.cpu().numpy()
        surf = pygame.surfarray.make_surface(sonuc_np)
        ekran.blit(surf, (0,0))
        
        frame_count += 1
        fps = frame_count / (gecen + 0.0001)
        kalan_sure = GPU_SHOW_SURESI - gecen
        yuzde = (gecen / GPU_SHOW_SURESI) * 100
        
        # Dashboard
        dashboard_ciz("GPU (Parallel Stream)", yuzde, fps, f"Render: {frame_count} Frame")
        pygame.display.flip()

    return frame_count / GPU_SHOW_SURESI

# --- ANA PROGRAM ---

def ana_menu():
    ekran.fill(RENK_ARKA)
    
    # Başlıklar
    baslik = font_dev.render("BENCHMARK ARENA", True, (255, 255, 255))
    ekran.blit(baslik, (GENISLIK//2 - baslik.get_width()//2, 100))
    
    # Menü Kutuları
    btn_cpu = pygame.Rect(GENISLIK//2 - 250, 300, 200, 100)
    btn_gpu = pygame.Rect(GENISLIK//2 + 50, 300, 200, 100)
    
    pygame.draw.rect(ekran, RENK_CPU_BAR, btn_cpu, border_radius=10)
    pygame.draw.rect(ekran, RENK_GPU_BAR, btn_gpu, border_radius=10)
    
    yazi1 = font_baslik.render("[1] CPU", True, (0,0,0))
    yazi2 = font_baslik.render("[2] GPU", True, (0,0,0))
    
    ekran.blit(yazi1, (btn_cpu.centerx - yazi1.get_width()//2, btn_cpu.centery - yazi1.get_height()//2))
    ekran.blit(yazi2, (btn_gpu.centerx - yazi2.get_width()//2, btn_gpu.centery - yazi2.get_height()//2))
    
    info = font_bilgi.render("Başlamak için 1 veya 2'ye basın. Çıkış için ESC.", True, (150, 150, 150))
    ekran.blit(info, (GENISLIK//2 - info.get_width()//2, 500))
    
    pygame.display.flip()

running = True
ana_menu()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                # CPU MODU BAŞLAT
                ekran.fill((0,0,0))
                # CPU işlemine giriyor...
                _, sure = sepia_filtresi_cpu_show(resim_array)
                
                # Sonuç Ekranı
                dashboard_ciz("CPU TAMAMLANDI", 100, 0, f"Toplam Süre: {sure:.2f} sn")
                pygame.display.flip()
                time.sleep(3) # Sonucu okumaları için bekle
                ana_menu()
                
            elif event.key == pygame.K_2:
                # GPU MODU BAŞLAT
                ekran.fill((0,0,0))
                load_msg = font_baslik.render("VRAM YÜKLENİYOR...", True, RENK_GPU_BAR)
                ekran.blit(load_msg, (GENISLIK//2 - 150, YUKSEKLIK//2))
                pygame.display.flip()
                
                # Tensor Hazırlığı
                device = "mps" if torch.backends.mps.is_available() else "cpu"
                tensor_img = torch.tensor(resim_array, device=device)
                
                # GPU Loop (Şovu uzatan kısım)
                avg_fps = gpu_show_loop(tensor_img)
                
                # Sonuç
                dashboard_ciz("GPU TAMAMLANDI", 100, avg_fps, "Test Bitti")
                pygame.display.flip()
                time.sleep(3)
                ana_menu()
            
            elif event.key == pygame.K_ESCAPE:
                running = False

pygame.quit()