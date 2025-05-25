# Disk Monitor

Harici diskleri izleyen ve bilgilerini kaydeden bir uygulama.

## Kurulum

### Geliştirici için:
1. Python 3.x kurulu olmalı
2. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Uygulamayı çalıştırın:
   ```bash
   python main.py
   ```

### Son Kullanıcı için:
1. `dist` klasöründeki `disk_monitor` dosyasını bilgisayarınıza kopyalayın
2. `start_monitor.sh` scriptini çalıştırın:
   ```bash
   ./start_monitor.sh
   ```

## Özellikler
- Harici diskleri otomatik tespit eder
- Disk bilgilerini JSON formatında kaydeder
- Gerçek zamanlı disk kullanımını gösterir
- Windows, Linux ve macOS desteği

## Loglar
Disk bilgileri `logs` klasöründe JSON formatında saklanır.
