import cv2
import subprocess
import socket
import threading
import numpy as np
import tkinter as tk
from tkinter import messagebox, ttk
import time
import datetime
import random
import traceback

class SenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gönderici Uygulaması")
        self.root.geometry("305x750")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        # Apply modern theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        style.configure("TEntry", font=("Helvetica", 10))
        style.configure("TRadiobutton", font=("Helvetica", 10))

        # Center content in a main frame
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # IP Inputs Frame
        self.ip_frame = ttk.LabelFrame(main_frame, text="Hedef IP'ler", padding="10 10 10 10")
        self.ip_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.ip_frame.columnconfigure(0, weight=1)
        ttk.Label(self.ip_frame, text="IP Adresleri:").grid(row=0, column=0, sticky="w", pady=2)
        self.ip_entries = []
        self.add_ip_entry()

        # IP Add/Remove Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky="ew", pady=5)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        ttk.Button(button_frame, text="IP Ekle", command=self.add_ip_entry).grid(row=0, column=0, padx=5, sticky="e")
        ttk.Button(button_frame, text="IP Sil", command=self.remove_ip_entry).grid(row=0, column=1, padx=5, sticky="w")

        # Port Input
        port_frame = ttk.Frame(main_frame)
        port_frame.grid(row=2, column=0, sticky="ew", pady=5)
        port_frame.columnconfigure(1, weight=1)
        ttk.Label(port_frame, text="Port:").grid(row=0, column=0, padx=10, sticky="e")
        self.port_entry = ttk.Entry(port_frame)
        self.port_entry.grid(row=0, column=1, padx=10, sticky="ew")

        # Protocol Selection
        protocol_frame = ttk.LabelFrame(main_frame, text="Protokol", padding="10 10 10 10")
        protocol_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        protocol_frame.columnconfigure(0, weight=1)
        protocol_frame.columnconfigure(1, weight=1)
        self.protocol_var = tk.StringVar(value="UDP")
        ttk.Radiobutton(protocol_frame, text="TCP", variable=self.protocol_var, value="TCP").grid(row=0, column=0, padx=5, sticky="w")
        ttk.Radiobutton(protocol_frame, text="UDP", variable=self.protocol_var, value="UDP").grid(row=0, column=1, padx=5, sticky="e")

        # Codec Selection
        codec_frame = ttk.LabelFrame(main_frame, text="Codec", padding="10 10 10 10")
        codec_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        codec_frame.columnconfigure(0, weight=1)
        codec_frame.columnconfigure(1, weight=1)
        self.codec_var = tk.StringVar(value="H.264")
        ttk.Radiobutton(codec_frame, text="H.264", variable=self.codec_var, value="H.264").grid(row=0, column=0, padx=5, sticky="w")
        ttk.Radiobutton(codec_frame, text="H.265", variable=self.codec_var, value="H.265").grid(row=0, column=1, padx=5, sticky="e")

        # Start/Stop Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, sticky="ew", pady=10)
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        self.start_button = ttk.Button(control_frame, text="Akışı Başlat", command=self.start_streaming)
        self.start_button.grid(row=0, column=0, padx=5, sticky="e")
        self.stop_button = ttk.Button(control_frame, text="Akışı Durdur", command=self.stop_streaming, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5, sticky="w")

        # Metrics Frame
        metrics_frame = ttk.LabelFrame(main_frame, text="Metrikler", padding="10 10 10 10")
        metrics_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=10)
        metrics_frame.columnconfigure(0, weight=1)

        self.latency_label = ttk.Label(metrics_frame, text="Gecikme: 0.00 ms")
        self.latency_label.grid(row=0, column=0, pady=2, sticky="w")
        self.frame_count_label = ttk.Label(metrics_frame, text="Gönderilen Kare: 0")
        self.frame_count_label.grid(row=1, column=0, pady=2, sticky="w")
        self.bitrate_label = ttk.Label(metrics_frame, text="Veri Akış Hızı: 0.00 Mbps")
        self.bitrate_label.grid(row=2, column=0, pady=2, sticky="w")
        self.packet_loss_label = ttk.Label(metrics_frame, text="Simüle Edilen Paket Kaybı: 0.00 %")
        self.packet_loss_label.grid(row=3, column=0, pady=2, sticky="w")
        self.jitter_label = ttk.Label(metrics_frame, text="Yerel Jitter: 0.00 ms")
        self.jitter_label.grid(row=4, column=0, pady=2, sticky="w")
        self.drop_frame_label = ttk.Label(metrics_frame, text="Simüle Edilen Kare Düşme Oranı: 0.00 %")
        self.drop_frame_label.grid(row=5, column=0, pady=2, sticky="w")

        # Initialize streaming variables
        self.proc = None
        self.socks = []
        self.dest_addrs = []
        self.running = False
        self.frame_count = 0
        self.sent_bytes = 0
        self.sent_packets = 0
        self.lost_packets = 0
        self.last_latency = 0
        self.last_jitter = 0
        self.dropped_frames = 0
        self.last_update = time.time()
        self.last_frame_time = None

    def add_ip_entry(self):
        """Add a new IP entry field."""
        try:
            row = len(self.ip_entries) + 1
            entry = ttk.Entry(self.ip_frame)
            entry.grid(row=row, column=0, pady=2, padx=5, sticky="ew")
            self.ip_entries.append(entry)
        except Exception as e:
            print(f"IP entry ekleme hatası: {traceback.format_exc()}")
            messagebox.showerror("Hata", f"IP girişi eklenemedi: {str(e)}")

    def remove_ip_entry(self):
        """Remove the last IP entry field."""
        try:
            if len(self.ip_entries) > 1:
                entry = self.ip_entries.pop()
                entry.destroy()
        except Exception as e:
            print(f"IP entry silme hatası: {traceback.format_exc()}")
            messagebox.showerror("Hata", f"IP girişi silinemedi: {str(e)}")

    def start_streaming(self):
        """Start the streaming process."""
        try:
            dest_ips = [entry.get().strip() for entry in self.ip_entries if entry.get().strip()]
            if not dest_ips:
                raise ValueError("En az bir geçerli IP girin.")
            port_str = self.port_entry.get().strip()
            if not port_str.isdigit():
                raise ValueError("Port geçerli bir sayı olmalı.")
            port = int(port_str)
            protocol = self.protocol_var.get()
            codec = self.codec_var.get()

            self.socks = []
            self.dest_addrs = []
            if protocol == "TCP":
                for ip in dest_ips:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        sock.connect((ip, port))
                        self.socks.append(sock)
                        print(f"Connected to {ip}:{port} via TCP")
                    except Exception as e:
                        print(f"Failed to connect to {ip}:{port}: {traceback.format_exc()}")
                if not self.socks:
                    raise ValueError("Hiçbir TCP bağlantısı kurulamadı.")
            else:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                for ip in dest_ips:
                    self.dest_addrs.append((ip, port))
                    print(f"Added UDP destination: {ip}:{port}")

            codec_option = "libx264" if codec == "H.264" else "libx265"
            command = [
                "ffmpeg",
                "-f", "rawvideo",
                "-pixel_format", "yuv420p",
                "-video_size", "1280x720",
                "-framerate", "30",
                "-i", "pipe:0",
                "-f", "dshow",
                "-i", "audio=Microphone Array (Realtek(R) Audio)",
                "-vf", "drawtext=text='%{localtime}':fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:x=10:y=10",
                "-c:v", codec_option,
                "-preset", "ultrafast",
                "-tune", "zerolatency",
                "-c:a", "aac",
                "-b:a", "128k",
                "-f", "mpegts",
                "pipe:1"
            ]

            self.proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("FFmpeg process started")

            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            ret, _ = self.cap.read()
            if not ret:
                raise ValueError("Kamera başlatılamadı. Erişim izni veya cihazı kontrol edin.")

            self.running = True
            self.start_time = time.time()
            self.last_update = self.start_time
            self.last_frame_time = self.start_time
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

            threading.Thread(target=self.capture_and_write, daemon=True).start()
            threading.Thread(target=self.read_and_send, daemon=True, args=(protocol,)).start()
            threading.Thread(target=self.log_ffmpeg_errors, daemon=True).start()

        except FileNotFoundError as e:
            print(f"FFmpeg bulunamadı: {traceback.format_exc()}")
            messagebox.showerror("Hata", "FFmpeg yüklü değil veya yolunda sorun var.")
        except ValueError as e:
            print(f"Değer hatası: {traceback.format_exc()}")
            messagebox.showerror("Hata", str(e))
        except OSError as e:
            print(f"Ağ/OS hatası: {traceback.format_exc()}")
            messagebox.showerror("Hata", f"Bağlantı hatası: {str(e)}")
        except Exception as e:
            print(f"Beklenmeyen hata (start_streaming): {traceback.format_exc()}")
            messagebox.showerror("Hata", f"Akış başlatılamadı: {str(e)}")

    def capture_and_write(self):
        """Capture frames from camera and write to FFmpeg pipe."""
        try:
            log_file = open("metrics.log", "a")
        except (IOError, PermissionError) as e:
            print(f"Log dosyası açma hatası: {traceback.format_exc()}")
            return
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Kare yakalama hatası")
                    break
                current_time = time.time()
                latency = (current_time - self.last_frame_time) * 1000 if self.last_frame_time else 0
                self.last_frame_time = current_time
                yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
                self.proc.stdin.write(yuv.tobytes())
                self.proc.stdin.flush()
                self.frame_count += 1
                self.frame_count_label.config(text=f"Gönderilen Kare: {self.frame_count}")
                self.latency_label.config(text=f"Gecikme: {latency:.2f} ms")
                log_file.write(f"Gönderici - Kare: {self.frame_count}, Gecikme: {latency:.2f} ms, Zaman: {datetime.datetime.now()}\n")
                log_file.flush()
        except BrokenPipeError as e:
            print(f"Pipe hatası (stdin): {traceback.format_exc()}")
        except Exception as e:
            print(f"Beklenmeyen hata (capture_and_write): {traceback.format_exc()}")
        finally:
            try:
                log_file.close()
            except Exception as e:
                print(f"Log dosyası kapatma hatası: {traceback.format_exc()}")

    def read_and_send(self, protocol):
        """Read from FFmpeg and send data to destinations."""
        last_time = time.time()
        while self.running:
            try:
                data = self.proc.stdout.read(1024)
                if not data:
                    print("FFmpeg'den veri okuma hatası veya sonlandı")
                    break
                start = time.time()
                if protocol == "TCP":
                    for i, sock in enumerate(self.socks[:]):
                        try:
                            sock.sendall(data)
                            self.sent_bytes += len(data)
                            self.sent_packets += 1
                            print(f"Sent {len(data)} bytes to TCP socket {i+1}")
                        except Exception as e:
                            print(f"Error sending to TCP socket {i+1}: {traceback.format_exc()}")
                            self.socks.pop(i)
                else:
                    for i, addr in enumerate(self.dest_addrs):
                        self.sock.sendto(data, addr)
                        self.sent_bytes += len(data)
                        self.sent_packets += 1
                        print(f"Sent {len(data)} bytes to UDP address {addr}")
                end = time.time()
                latency = (end - start) * 1000
                jitter = abs(latency - self.last_latency) if self.last_latency else 0
                self.last_jitter = jitter  
                self.last_latency = latency 
                if random.random() < 0.01:
                    self.lost_packets += 1
                if random.random() < 0.005:
                    self.dropped_frames += 1
                if time.time() - last_time > 1:
                    interval = time.time() - self.last_update
                    bitrate = round((self.sent_bytes * 8) / (1024 * 1024) / max(interval, 0.001), 2)
                    packet_loss = round((self.lost_packets / max(1, self.sent_packets)) * 100, 2)
                    drop_rate = round((self.dropped_frames / max(1, self.frame_count)) * 100, 2)
                    self.bitrate_label.config(text=f"Veri Akış Hızı: {bitrate:.2f} Mbps")
                    self.packet_loss_label.config(text=f"Simüle Edilen Paket Kaybı: {packet_loss:.2f} %")
                    self.jitter_label.config(text=f"Yerel Jitter: {jitter:.2f} ms")
                    self.drop_frame_label.config(text=f"Simüle Edilen Kare Düşme Oranı: {drop_rate:.2f} %")
                    self.last_update = time.time()
                    self.sent_bytes = 0
                    self.sent_packets = 0
                    self.lost_packets = 0
                    self.dropped_frames = 0
                    last_time = time.time()
            except IOError as e:
                print(f"IO hatası (stdout read): {traceback.format_exc()}")
                break
            except Exception as e:
                print(f"Beklenmeyen hata (read_and_send): {traceback.format_exc()}")
                break

    def log_ffmpeg_errors(self):
        """Log FFmpeg errors from stderr."""
        while self.running:
            try:
                error = self.proc.stderr.readline()
                if error:
                    print(f"FFmpeg Hatası: {error.decode().strip()}")
            except Exception as e:
                print(f"FFmpeg error loglama hatası: {traceback.format_exc()}")
                break

    def stop_streaming(self):
        """Stop the streaming and clean up resources."""
        self.running = False
        try:
            if self.proc:
                self.proc.stdin.close()
                self.proc.terminate()
                self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("FFmpeg terminate timeout, killing process")
            self.proc.kill()
        except Exception as e:
            print(f"FFmpeg kapatma hatası: {traceback.format_exc()}")
        protocol = self.protocol_var.get()
        try:
            if protocol == "TCP":
                for sock in self.socks:
                    sock.close()
            else:
                if hasattr(self, 'sock') and self.sock:
                    self.sock.close()
        except Exception as e:
            print(f"Socket kapatma hatası: {traceback.format_exc()}")
        try:
            if self.cap:
                self.cap.release()
        except Exception as e:
            print(f"Kamera release hatası: {traceback.format_exc()}")
        self.socks = []
        self.dest_addrs = []
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SenderApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Ana uygulama hatası: {traceback.format_exc()}")