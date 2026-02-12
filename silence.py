#!/usr/bin/env python3
"""
Gelişmiş Stenografi Tool - PNG ve BMP dosyalarına mesaj/dosya gömme ve çıkarma aracı
"""

import sys
from PIL import Image
import numpy as np
import os
import base64
import json

class AdvancedStegoTool:
    def __init__(self):
        self.delimiter = "<<<END_OF_STEGO_DATA>>>"
        self.supported_formats = ['.png', '.bmp']
    
    def encode_text(self, image_path, text, output_path):
        """
        Resme metin mesajı gömer
        """
        data = {
            'type': 'text',
            'content': text
        }
        self._encode_data(image_path, data, output_path)
        print(f"✓ Metin mesajı başarıyla gömüldü: {output_path}")
        print(f"  Mesaj uzunluğu: {len(text)} karakter")
    
    def encode_file(self, image_path, file_path, output_path):
        """
        Resme dosya gömer (binary olarak)
        """
        # Dosya kontrolü
        if not os.path.exists(file_path):
            raise ValueError(f"Dosya bulunamadı: {file_path}")
        
        # Dosyayı oku
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Base64 encode et
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        # Metadata hazırla
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_path)[1]
        
        data = {
            'type': 'file',
            'filename': file_name,
            'extension': file_ext,
            'content': encoded_content,
            'size': len(file_content)
        }
        
        self._encode_data(image_path, data, output_path)
        print(f"✓ Dosya başarıyla gömüldü: {output_path}")
        print(f"  Dosya adı: {file_name}")
        print(f"  Dosya boyutu: {len(file_content)} bytes")
        print(f"  Dosya tipi: {file_ext if file_ext else 'uzantısız'}")
    
    def _encode_data(self, image_path, data_dict, output_path):
        """
        Resme JSON formatında data gömer (LSB yöntemi ile)
        """
        # Dosya uzantısını kontrol et
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in self.supported_formats:
            raise ValueError(f"Sadece {', '.join(self.supported_formats)} dosyaları desteklenir!")
        
        # Resmi aç
        img = Image.open(image_path)
        
        # RGB moduna çevir
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resmi numpy array'e çevir
        img_array = np.array(img)
        
        # Data'yı JSON'a çevir
        json_data = json.dumps(data_dict)
        message_with_delimiter = json_data + self.delimiter
        
        # Binary'ye çevir
        binary_message = ''.join(format(ord(char), '08b') for char in message_with_delimiter)
        
        # Mesajın sığıp sığmayacağını kontrol et
        max_bytes = img_array.size
        required_bytes = len(binary_message)
        
        if required_bytes > max_bytes:
            max_chars = max_bytes // 8
            raise ValueError(
                f"Veri çok büyük! Resim maksimum {max_chars} karakter (yaklaşık {max_chars} byte) alabilir.\n"
                f"Gereken: {required_bytes // 8} karakter\n"
                f"Öneri: Daha büyük bir resim kullanın veya dosyayı sıkıştırın."
            )
        
        # Veriyi piksellere göm
        flat_img = img_array.flatten()
        
        for i, bit in enumerate(binary_message):
            # LSB'yi (en az anlamlı bit) değiştir
            flat_img[i] = (flat_img[i] & 0xFE) | int(bit)
        
        # Array'i yeniden şekillendir
        encoded_img_array = flat_img.reshape(img_array.shape)
        
        # Yeni resmi kaydet
        encoded_img = Image.fromarray(encoded_img_array.astype('uint8'), 'RGB')
        
        # Çıktı formatını belirle
        output_ext = os.path.splitext(output_path)[1].lower()
        if output_ext == '.png':
            encoded_img.save(output_path, 'PNG')
        elif output_ext == '.bmp':
            encoded_img.save(output_path, 'BMP')
        else:
            raise ValueError("Çıktı dosyası PNG veya BMP formatında olmalı!")
    
    def decode_data(self, image_path, output_path=None):
        """
        Resimden veriyi çıkarır
        """
        # Dosya uzantısını kontrol et
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in self.supported_formats:
            raise ValueError(f"Sadece {', '.join(self.supported_formats)} dosyaları desteklenir!")
        
        # Resmi aç
        img = Image.open(image_path)
        
        # RGB moduna çevir
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resmi numpy array'e çevir
        img_array = np.array(img)
        
        # Düzleştirilmiş array
        flat_img = img_array.flatten()
        
        # Binary mesajı çıkar
        binary_message = ''
        for pixel_value in flat_img:
            binary_message += str(pixel_value & 1)
        
        # Binary'yi karakterlere çevir
        json_str = ''
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i+8]
            if len(byte) == 8:
                char = chr(int(byte, 2))
                json_str += char
                
                # Delimiter'ı bulduk mu?
                if json_str.endswith(self.delimiter):
                    json_str = json_str[:-len(self.delimiter)]
                    
                    # JSON'u parse et
                    try:
                        data = json.loads(json_str)
                    except json.JSONDecodeError:
                        raise ValueError("Resimde geçerli stenografi verisi bulunamadı!")
                    
                    # Veri tipine göre işle
                    if data['type'] == 'text':
                        print("\n" + "="*70)
                        print("GİZLİ MESAJ (METİN):")
                        print("="*70)
                        print(data['content'])
                        print("="*70 + "\n")
                        return data['content']
                    
                    elif data['type'] == 'file':
                        # Base64 decode et
                        file_content = base64.b64decode(data['content'])
                        
                        # Çıktı dosya adını belirle
                        if output_path is None:
                            output_path = data['filename']
                        
                        # Dosyayı kaydet
                        with open(output_path, 'wb') as f:
                            f.write(file_content)
                        
                        print("\n" + "="*70)
                        print("GİZLİ DOSYA ÇIKARILDI:")
                        print("="*70)
                        print(f"Dosya adı: {data['filename']}")
                        print(f"Dosya tipi: {data['extension'] if data['extension'] else 'uzantısız'}")
                        print(f"Dosya boyutu: {data['size']} bytes")
                        print(f"Kaydedildi: {output_path}")
                        print("="*70 + "\n")
                        
                        # Eğer text dosyası ise içeriğini de göster
                        text_extensions = ['.txt', '.c', '.cs', '.cpp', '.h', '.py', '.js', 
                                         '.java', '.php', '.rb', '.go', '.rs', '.sh', 
                                         '.bat', '.ps1', '.html', '.css', '.xml', '.json']
                        
                        if data['extension'].lower() in text_extensions:
                            try:
                                content_preview = file_content.decode('utf-8')
                                print("DOSYA İÇERİĞİ ÖNIZLEME:")
                                print("-" * 70)
                                # İlk 50 satırı göster
                                lines = content_preview.split('\n')
                                preview_lines = lines[:50]
                                print('\n'.join(preview_lines))
                                if len(lines) > 50:
                                    print(f"\n... ({len(lines) - 50} satır daha var)")
                                print("-" * 70 + "\n")
                            except:
                                pass
                        
                        return output_path
        
        raise ValueError("Resimde gizli veri bulunamadı!")
    
    def get_image_capacity(self, image_path):
        """
        Resmin kaç byte veri alabileceğini hesaplar
        """
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in self.supported_formats:
            raise ValueError(f"Sadece {', '.join(self.supported_formats)} dosyaları desteklenir!")
        
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        max_bytes = img_array.size // 8
        
        return max_bytes

def print_usage():
    """
    Kullanım talimatlarını yazdır
    """
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           GELİŞMİŞ STENOGRAFI TOOL - PNG & BMP                       ║
║           Mesaj ve Dosya Gömme Aracı                                 ║
╚══════════════════════════════════════════════════════════════════════╝

KULLANIM:

  1. METİN MESAJI GÖMME:
     python advanced_stego.py encode-text <resim> <çıktı> "Gizli mesaj"
     
     Örnek:
     python advanced_stego.py encode-text foto.png gizli.png "Parola: ABC123"
     
  2. DOSYA GÖMME:
     python advanced_stego.py encode-file <resim> <gömülecek_dosya> <çıktı>
     
     Örnekler:
     python advanced_stego.py encode-file foto.png script.py gizli.png
     python advanced_stego.py encode-file foto.bmp program.c gizli.bmp
     python advanced_stego.py encode-file resim.png data.json output.png
     
  3. VERİ ÇIKARMA:
     python advanced_stego.py decode <resim> [çıktı_dosyası]
     
     Örnekler:
     python advanced_stego.py decode gizli.png
     python advanced_stego.py decode gizli.png extracted_file.c
     
  4. RESİM KAPASİTESİ KONTROLÜ:
     python advanced_stego.py capacity <resim>
     
     Örnek:
     python advanced_stego.py capacity foto.png

DESTEKLENEN DOSYA TİPLERİ:
  • Programlama: .c, .cs, .cpp, .h, .py, .js, .java, .php, .go, .rs
  • Script: .sh, .bat, .ps1
  • Markup: .html, .xml, .json, .css
  • Veri: .txt, .csv, .sql
  • Binary: Herhangi bir dosya türü!

NOTLAR:
  • Dosya boyutu resim kapasitesine bağlıdır
  • Büyük dosyalar için büyük resim kullanın
  • Metin dosyalarının içeriği decode sırasında önizlenir
    """)

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    stego = AdvancedStegoTool()
    command = sys.argv[1].lower()
    
    try:
        if command == 'encode-text':
            if len(sys.argv) < 5:
                print("❌ Hata: encode-text için gerekli parametreler eksik!")
                print("Kullanım: python advanced_stego.py encode-text <resim> <çıktı> \"mesaj\"")
                sys.exit(1)
            
            input_image = sys.argv[2]
            output_image = sys.argv[3]
            message = sys.argv[4]
            
            if not os.path.exists(input_image):
                print(f"❌ Hata: {input_image} dosyası bulunamadı!")
                sys.exit(1)
            
            stego.encode_text(input_image, message, output_image)
            
        elif command == 'encode-file':
            if len(sys.argv) < 5:
                print("❌ Hata: encode-file için gerekli parametreler eksik!")
                print("Kullanım: python advanced_stego.py encode-file <resim> <dosya> <çıktı>")
                sys.exit(1)
            
            input_image = sys.argv[2]
            input_file = sys.argv[3]
            output_image = sys.argv[4]
            
            if not os.path.exists(input_image):
                print(f"❌ Hata: {input_image} dosyası bulunamadı!")
                sys.exit(1)
            
            if not os.path.exists(input_file):
                print(f"❌ Hata: {input_file} dosyası bulunamadı!")
                sys.exit(1)
            
            stego.encode_file(input_image, input_file, output_image)
            
        elif command == 'decode':
            if len(sys.argv) < 3:
                print("❌ Hata: decode için resim parametresi eksik!")
                print("Kullanım: python advanced_stego.py decode <resim> [çıktı_dosyası]")
                sys.exit(1)
            
            input_image = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            
            if not os.path.exists(input_image):
                print(f"❌ Hata: {input_image} dosyası bulunamadı!")
                sys.exit(1)
            
            stego.decode_data(input_image, output_file)
            
        elif command == 'capacity':
            if len(sys.argv) < 3:
                print("❌ Hata: capacity için resim parametresi eksik!")
                print("Kullanım: python advanced_stego.py capacity <resim>")
                sys.exit(1)
            
            input_image = sys.argv[2]
            
            if not os.path.exists(input_image):
                print(f"❌ Hata: {input_image} dosyası bulunamadı!")
                sys.exit(1)
            
            capacity = stego.get_image_capacity(input_image)
            print(f"\n{'='*60}")
            print(f"RESİM KAPASİTE BİLGİSİ: {os.path.basename(input_image)}")
            print(f"{'='*60}")
            print(f"Maksimum veri kapasitesi: {capacity:,} bytes")
            print(f"                          {capacity / 1024:.2f} KB")
            if capacity > 1024 * 1024:
                print(f"                          {capacity / (1024 * 1024):.2f} MB")
            print(f"{'='*60}\n")
            
        else:
            print(f"❌ Bilinmeyen komut: {command}")
            print_usage()
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
