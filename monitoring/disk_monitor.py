import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import json
import platform
from disk_utils.get_external_disks import get_external_disks
from monitoring.save_disk_contents import save_disk_contents

class DiskChangeHandler(FileSystemEventHandler):
    def __init__(self, disk_info):
        self.disk_info = disk_info
        self.last_scan = datetime.now()
        self.scan_cooldown = 5  # Minimum seconds between scans

    def on_any_event(self, event):
        # Prevent too frequent scans
        if (datetime.now() - self.last_scan).total_seconds() < self.scan_cooldown:
            return

        print(f"\nDisk değişikliği algılandı: {event.event_type} - {event.src_path}")
        self.last_scan = datetime.now()

        # Yeniden loglama işlemi
        save_disk_contents(self.disk_info)

class DiskMonitor:
    def __init__(self):
        self.observers = []
        self.monitored_disks = set()

    def start_monitoring(self):
        # Başlangıçta takılı olan tüm diskleri tara ve logla
        initial_disks = get_external_disks()
        if initial_disks:
            print("\nBaşlangıçta takılı olan diskler taranıyor...")
            for disk in initial_disks:
                print(f"\nDisk taranıyor: {disk['label']} ({disk['mountpoint']})")
                save_disk_contents(disk)
                self.monitored_disks.add(disk['disk_id'])
                self._start_disk_monitoring(disk)
        else:
            print("\nTakılı disk bulunamadı.")

        # Sürekli disk değişikliklerini izle
        while True:
            try:
                current_disks = get_external_disks()
                current_disk_ids = {disk['disk_id'] for disk in current_disks}

                # Yeni diskleri izlemeye başla
                for disk in current_disks:
                    if disk['disk_id'] not in self.monitored_disks:
                        print(f"\nYeni disk algılandı: {disk['label']} ({disk['mountpoint']})")
                        save_disk_contents(disk)
                        self._start_disk_monitoring(disk)
                        self.monitored_disks.add(disk['disk_id'])

                # Çıkarılan diskleri izlemeyi durdur
                removed_disks = self.monitored_disks - current_disk_ids
                for disk_id in removed_disks:
                    self._stop_disk_monitoring(disk_id)
                    self.monitored_disks.remove(disk_id)

                time.sleep(1)  # CPU kullanımını azaltmak için kısa bekleme

            except KeyboardInterrupt:
                self.stop_all_monitoring()
                break
            except Exception as e:
                print(f"Hata oluştu: {str(e)}")
                time.sleep(5)  # Hata durumunda bekle

    def _start_disk_monitoring(self, disk_info):
        event_handler = DiskChangeHandler(disk_info)
        observer = Observer()
        observer.schedule(event_handler, disk_info['mountpoint'], recursive=True)
        observer.start()
        self.observers.append((disk_info['disk_id'], observer))
        print(f"\nDisk izlenmeye başlandı: {disk_info['label']} ({disk_info['mountpoint']})")

    def _stop_disk_monitoring(self, disk_id):
        for idx, (monitored_id, observer) in enumerate(self.observers):
            if monitored_id == disk_id:
                observer.stop()
                observer.join()
                self.observers.pop(idx)
                print(f"\nDisk izleme durduruldu: {disk_id}")
                break

    def stop_all_monitoring(self):
        for _, observer in self.observers:
            observer.stop()
            observer.join()
        self.observers.clear()
        self.monitored_disks.clear()
        print("\nTüm disk izleme işlemleri durduruldu.")

