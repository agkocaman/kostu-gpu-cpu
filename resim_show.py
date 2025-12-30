import pygame
import random
import sys
import time
import numpy as np

# --- AYARLAR ---
EKRAN_GEN = 1200
EKRAN_YUK = 800
RESIM_ADI = "resim.jpg"

# SİMÜLASYON AYARLARI
CPU_ADIM = 30        # CPU görselleştirme hızı (Daha yüksek = Daha hızlı güncelleme)
GPU_PARALEL = 400    # GPU'nun aynı anda attığı piksel sayısı

# RENK PALETİ (Modern Dark Theme)
RENK_BG = (30, 33, 40)          # Ana Arka Plan
RENK_PANEL = (40, 44, 52)       # Panel Rengi
RENK_BTN_CPU = (231, 76, 60)    # Alizarin Red
RENK_BTN_GPU = (52, 152, 219)   # Peter River Blue
RENK_BTN_HOVER = (255, 255, 255)# Buton üzerine gelince
RENK_TEXT = (236, 240, 241)     # Clouds
RENK_PIXEL_CPU = (46, 204, 113) # Emerald Green (İmleç)
RENK_PIXEL_GPU = (0, 255, 255)  # Cyan (İmleç)

pygame.init()
ekran = pygame.display.set_mode((EKRAN_GEN, EKRAN_YUK))
pygame.display.set_caption("CPU vs GPU Mimari Simülasyonu v2.0")

# Fontlar
font_baslik = pygame.font.SysFont('Segoe UI', 40, bold=True)
font_btn = pygame.font.SysFont('Segoe UI', 24, bold=True)
font_bilgi = pygame.font.SysFont('Consolas', 16)

# --- RESİM İŞLEME ---
def resim_yukle():
    try:
        ham = pygame.image.load(RESIM_ADI)
        # Sunum için ideal boyut (çok büyük olursa simülasyon çok uzun sürer)
        hedef_boyut = (600, 400)
        resim = pygame.transform.scale(ham, hedef_boyut)
        data = pygame.surfarray.array3d(resim)
        return resim, data, hedef_boyut[0], hedef_boyut[1]
    except:
        # Resim yoksa otomatik desen oluştur
        w, h = 600, 400
        data = np.zeros((w, h, 3), dtype=int)
        for x in range(w):
            for y in range(h): data[x,y] = [(x*y)%255, (x+y)%255, y%255]
        return None, data, w, h

_, pixel_data, w, h = resim_yukle()
off_x = (EKRAN_GEN - w) // 2
off_y = (EKRAN_YUK - h) // 2

# --- ARAYÜZ ELEMANLARI ---

def buton_ciz(rect, text, ana_renk, aktif_mi=False):
    """Mouse üzerine gelince parlayan buton çizer"""
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)
    
    renk = ana_renk
    if is_hovered and aktif_mi:
        renk = [min(c + 30, 255) for c in ana_renk] # Rengi aç
    
    # Gölge
    pygame.draw.rect(ekran, (20,20,20), (rect.x+4, rect.y+4, rect.w, rect.h), border_radius=12)
    # Ana Buton
    pygame.draw.rect(ekran, renk, rect, border_radius=12)
    # Çerçeve
    pygame.draw.rect(ekran, (255,255,255) if is_hovered else (100,100,100), rect, 2, border_radius=12)
    
    txt_surf = font_btn.render(text, True, RENK_TEXT)
    ekran.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))
    
    return is_hovered and pygame.mouse.get_pressed()[0]

def geri_buton_kontrol():
    """Simülasyon sırasında geri dönmek için buton"""
    btn_rect = pygame.Rect(20, 20, 100, 40)
    if buton_ciz(btn_rect, "< GERİ", (80, 80, 80), True):
        return True
    return False

# --- SİMÜLASYONLAR ---

def cpu_modu():
    canvas = pygame.Surface((w, h))
    canvas.fill((0,0,0))
    running = True
    count = 0
    
    # CPU için iterator (x, y)
    iterator = ((x, y) for y in range(h) for x in range(w))
    
    while running:
        ekran.fill(RENK_BG)
        # Başlık ve Çerçeve
        title = font_baslik.render("CPU: SERIAL PROCESSING", True, RENK_BTN_CPU)
        ekran.blit(title, (EKRAN_GEN//2 - title.get_width()//2, 50))
        pygame.draw.rect(ekran, (50,50,50), (off_x-5, off_y-5, w+10, h+10), 2)
        
        # Geri Butonu
        if geri_buton_kontrol(): return
        
        # Simülasyon Adımı
        for _ in range(CPU_ADIM):
            try:
                x, y = next(iterator)
                r, g, b = pixel_data[x, y]
                canvas.set_at((x, y), (r, g, b))
                
                # Sadece son işlenen pikseli işaretle (Yeşil İmleç)
                last_x, last_y = x, y
            except StopIteration:
                break
        
        ekran.blit(canvas, (off_x, off_y))
        
        # CPU İmleci (Büyütülmüş)
        if 'last_x' in locals():
            pygame.draw.rect(ekran, RENK_PIXEL_CPU, (off_x + last_x, off_y + last_y, 4, 4))
            
        # İstatistik
        txt_stat = font_bilgi.render("Tek Çekirdek: Pikseller sırayla işleniyor...", True, (150,150,150))
        ekran.blit(txt_stat, (off_x, off_y + h + 20))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

def gpu_modu():
    canvas = pygame.Surface((w, h))
    canvas.fill((0,0,0))
    running = True
    
    # Koordinatları karıştır (Paralel erişim simülasyonu)
    coords = [(x, y) for x in range(w) for y in range(h)]
    random.shuffle(coords)
    
    idx = 0
    total = len(coords)
    
    while running:
        ekran.fill(RENK_BG)
        title = font_baslik.render("GPU: PARALLEL PROCESSING", True, RENK_BTN_GPU)
        ekran.blit(title, (EKRAN_GEN//2 - title.get_width()//2, 50))
        pygame.draw.rect(ekran, (50,50,50), (off_x-5, off_y-5, w+10, h+10), 2)

        if geri_buton_kontrol(): return
        
        # Simülasyon Adımı (Toplu İşlem)
        batch_coords = []
        if idx < total:
            end_idx = min(idx + GPU_PARALEL, total)
            batch = coords[idx : end_idx]
            
            for bx, by in batch:
                r, g, b = pixel_data[bx, by]
                canvas.set_at((bx, by), (r, g, b))
                batch_coords.append((bx, by))
            
            idx = end_idx
        
        ekran.blit(canvas, (off_x, off_y))
        
        # GPU İmleçleri (Mavi yağmur)
        for bx, by in batch_coords:
            ekran.set_at((off_x+bx, off_y+by), RENK_PIXEL_GPU)
            # Parlama efekti
            if random.random() > 0.8:
                ekran.set_at((off_x+bx+1, off_y+by), (255,255,255))
        
        txt_stat = font_bilgi.render(f"Binlerce Çekirdek: Aynı anda {GPU_PARALEL} piksel işleniyor...", True, (150,150,150))
        ekran.blit(txt_stat, (off_x, off_y + h + 20))
        
        pygame.display.flip()
        
        # GPU çok hızlı bitmesin diye minik gecikme (insan gözü görsün diye)
        # time.sleep(0.002)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

# --- ANA MENÜ ---
def main_menu():
    btn_cpu_rect = pygame.Rect(EKRAN_GEN//2 - 250, EKRAN_YUK//2, 220, 80)
    btn_gpu_rect = pygame.Rect(EKRAN_GEN//2 + 30, EKRAN_YUK//2, 220, 80)
    
    while True:
        ekran.fill(RENK_BG)
        
        # Logo / Başlık
        head = font_baslik.render("PIXEL RENDER BENCHMARK", True, RENK_TEXT)
        sub = font_bilgi.render("Mimari Farklılıkları Eğitim Simülasyonu", True, (150,150,150))
        ekran.blit(head, (EKRAN_GEN//2 - head.get_width()//2, 200))
        ekran.blit(sub, (EKRAN_GEN//2 - sub.get_width()//2, 250))
        
        # Butonlar (Tıklama Kontrolü ile)
        mouse_down = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN: mouse_down = True
        
        # CPU Butonu Çiz ve Kontrol Et
        if buton_ciz(btn_cpu_rect, "CPU BAŞLAT", RENK_BTN_CPU, True):
            if mouse_down: cpu_modu()
            
        # GPU Butonu Çiz ve Kontrol Et
        if buton_ciz(btn_gpu_rect, "GPU BAŞLAT", RENK_BTN_GPU, True):
             if mouse_down: gpu_modu()
        
        # Alt Bilgi
        info = font_bilgi.render("Mühendislik Sunumu İçin Hazırlanmıştır", True, (80,80,90))
        ekran.blit(info, (EKRAN_GEN//2 - info.get_width()//2, EKRAN_YUK - 50))
        
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
