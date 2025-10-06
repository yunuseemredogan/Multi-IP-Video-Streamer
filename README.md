# Multi IP Video Streamer 🚀

<img width="1145" height="802" alt="video-streaming" src="https://github.com/user-attachments/assets/065b5b6a-1ab4-44a9-ac21-9ca0835896ce" />

## 📖 Overview
Multi-IP-Video-Streamer is a Python-based desktop application that allows users to capture live video from a webcam and audio from a microphone, encode the stream using FFmpeg, and send it to one or multiple target IP addresses over TCP or UDP protocols. The app features a user-friendly GUI built with Tkinter, making it easy to configure streaming settings like IP addresses, ports, protocols, and codecs (H.264 or H.265).

This project is particularly useful for:
- Testing network streaming setups, such as in IoT devices, remote monitoring, or video conferencing prototypes.
- Simulating real-world streaming scenarios with built-in metrics for latency, bitrate, packet loss, jitter, and frame drops.
- Educational purposes, demonstrating how to integrate computer vision (OpenCV), media encoding (FFmpeg), networking (sockets), and multi-threading in Python.

The core idea is to provide a "sender" tool for video/audio streaming without relying on cloud services—everything runs locally on your machine. It emphasizes low-latency performance with FFmpeg optimizations and includes error handling for robustness. Note: This is a sender-only application; you'll need a receiver (e.g., VLC or a custom script) on the target IPs to view the stream.

## ✨ Key Features
- **Multi-Destination Streaming**: Add/remove multiple IP addresses dynamically and stream to all simultaneously. 📡
- **Protocol Flexibility**: Choose TCP for reliable delivery or UDP for faster, lower-latency transmission (with potential packet loss). 🔄
- **Codec Options**: Select H.264 (libx264) for broad compatibility or H.265 (libx265) for better compression. 🎥
- **Real-Time Metrics Dashboard**: Monitor latency (ms), frame count, bitrate (Mbps), simulated packet loss (%), jitter (ms), and frame drop rate (%) right in the GUI. 📊
- **Timestamp Overlay**: Automatically adds the current local time to the video feed for easy synchronization and logging. ⏰
- **Simulation of Network Issues**: Randomly simulates packet loss (1% chance) and frame drops (0.5% chance) to mimic real-world conditions without actual network interference. 🌐
- **Logging and Error Handling**: Logs metrics to a file (`metrics.log`) and handles exceptions with user-friendly message boxes and console output. 📝
- **Threaded Architecture**: Uses multi-threading for non-blocking capture, encoding, sending, and error logging to ensure smooth performance. 🧵
- **Customizable Resolution and FPS**: Fixed at 1280x720 @ 30 FPS in code, but easily modifiable for different needs.

## 📋 Requirements
To run this code, your system must meet the following prerequisites. The app is designed for Windows due to the audio capture method, but can be adapted for Linux/macOS with minor changes.

### Software Dependencies:
- **Python 3.6+**: The app uses standard Python libraries plus a few external ones. Download from [python.org](https://www.python.org/downloads/). 🐍
- **FFmpeg**: Essential for encoding video/audio. Download the latest build from [ffmpeg.org/download.html](https://ffmpeg.org/download.html) and add it to your system's PATH environment variable. Test by running `ffmpeg -version` in your terminal. Without this, the app won't start streaming. 🎞️
- **Python Libraries**:
  - `opencv-python`: For webcam capture (install via `pip install opencv-python`).
  - `numpy`: Automatically installed with OpenCV, used for frame processing.
  - `tkinter`: Built-in with Python (ensure it's enabled during Python installation on Windows).
  - Other built-ins: `subprocess` (for FFmpeg), `socket` (networking), `threading` (multi-threading), `time`, `datetime`, `random`, `traceback` (error handling).

No additional pip installs are needed beyond OpenCV, as everything else is standard.

### Hardware Requirements:
- **Webcam**: Any standard camera (built-in or external) accessible via OpenCV (device index 0 by default).
- **Microphone**: Required for audio capture. The code uses "Microphone Array (Realtek(R) Audio)"—change this in the FFmpeg command if your device differs.
- **Network**: Local network access for streaming to target IPs. Ensure firewalls allow traffic on the chosen port.

**Platform Notes**: Audio input uses DirectShow (`dshow`), which is Windows-specific. For Linux, replace with `alsa` (e.g., `-f alsa -i default`); for macOS, use `avfoundation`.

## 🛠️ Installation
Follow these steps to get the project up and running on your local machine.

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yunuseemredogan/Multi-IP-Video-Streamer.git
   cd MultiIPVideoStreamer
   ```
   This downloads the entire project, including the main Python script (e.g., name it `sender_app.py`).

2. **Install Python Dependencies**:
   Open a terminal in the project folder and run:
   ```bash
   pip install opencv-python
   ```
   If you're using a virtual environment (recommended), create one first:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/macOS
   venv\Scripts\activate     # On Windows
   ```

3. **Install FFmpeg**:
   - Download and extract the FFmpeg binaries.
   - Add the `bin` folder to your PATH (e.g., on Windows: System Properties > Environment Variables > Edit PATH).
   - Verify: `ffmpeg -version` should output version info.

4. **Optional: Create a Screenshots Folder**:
   If you want to add images to this README, create a `screenshots` folder and upload GUI captures.

## ▶️ Usage
Running the app is straightforward once installed.

1. **Launch the Application**:
   In the project folder, run:
   ```bash
   python sender_app.py  # Replace with your script name if different
   ```
   This opens the GUI window titled "Gönderici Uygulaması" (Sender Application).

2. **Configure Settings in the GUI**:
   - **IP Addresses**: Click "IP Ekle" to add fields, enter IPs (e.g., 192.168.1.100), and "IP Sil" to remove. At least one valid IP is required.
   - **Port**: Enter a numeric port (e.g., 5000). Ensure the receiver is listening on this port.
   - **Protocol**: Select TCP (reliable) or UDP (fast).
   - **Codec**: Choose H.264 (compatible) or H.265 (efficient).
   - Click "Akışı Başlat" (Start Stream) to begin.

3. **Monitor and Stop**:
   - Watch metrics update in real-time (e.g., latency, bitrate).
   - Click "Akışı Durdur" (Stop Stream) to end safely—this closes resources like sockets and the camera.

4. **Receiver Setup** (Not Included in This Repo):
   - Use VLC: Open Network Stream with `tcp://@:5000` or `udp://@:5000`.
   - Or FFmpeg: `ffmpeg -i tcp://0.0.0.0:5000 -f sdl "Video Stream"`.
   - For multiple receivers, run on each target machine.

**Pro Tip**: Test locally first by using `127.0.0.1` as IP and running a receiver on the same machine.

## 🔍 How It Works: The Inner Mechanics
The app captures, encodes, and streams in a pipeline fashion, using threads for efficiency. Here's a detailed breakdown.

### High-Level Workflow (ASCII Diagram):
```
+-------------------+   Pipe   +-------------------+   Network   +-------------------+
| Webcam + Mic      | --------> | FFmpeg Encoding   | ----------> | Sockets (TCP/UDP) |
| (OpenCV Capture)  |         | (H.264/H.265 +    |             | to Multiple IPs   |
|                   |         | Timestamp + Audio)|             | + Metrics Sim.    |
+-------------------+         +-------------------+             +-------------------+
  |                                         |                          |
  v                                         v                          v
Metrics Logging (file)                  GUI Updates                Error Logging (console)
```

1. **Initialization**:
   - GUI setup with Tkinter (ttk for modern styling): Frames for IPs, port, radios, buttons, and metrics labels.
   - Variables: Streaming flags (`running`), counters (frames, bytes, packets), sockets list.

2. **Starting the Stream** (`start_streaming` method):
   - Validate inputs (IPs, port).
   - Create sockets: TCP connects individually; UDP uses one socket with multiple destinations.
   - Build FFmpeg command: Pipes raw video from stdin, adds audio, overlays timestamp, encodes, outputs MPEG-TS to stdout.
   - Launch FFmpeg as subprocess.
   - Open webcam with OpenCV.
   - Start threads: Capture/write, read/send, log errors.

3. **Capture and Write Thread** (`capture_and_write`):
   - Loop: Read frame from camera, convert to YUV420P, write to FFmpeg stdin.
   - Update frame count, calculate latency (time between frames).
   - Log to `metrics.log` (e.g., "Gönderici - Kare: 1, Gecikme: 10.00 ms").

4. **Read and Send Thread** (`read_and_send`):
   - Loop: Read encoded data from FFmpeg stdout (1024-byte chunks).
   - Send via sockets (TCP: `sendall`; UDP: `sendto`).
   - Calculate metrics: Latency/jitter per send, bitrate every second.
   - Simulate issues: Random packet loss/drop, update labels.

5. **Error Logging Thread** (`log_ffmpeg_errors`):
   - Read FFmpeg stderr, print errors (e.g., encoding issues).

6. **Stopping the Stream** (`stop_streaming`):
   - Set `running=False`, close pipes, terminate FFmpeg, close sockets, release camera.

The app runs on a fixed 1280x720 @ 30 FPS, but you can tweak in code (e.g., `cap.set` or FFmpeg args). It uses `ultrafast` preset for low latency.

## 🧱 Code Structure
The code is in one file for simplicity, as a `SenderApp` class inheriting from nothing (pure composition).

- **Imports**: Grouped by function (cv2/subprocess/socket/threading/np/tk/ttk/time/datetime/random/traceback).
- **Class `__init__`**: Sets up GUI elements, styles, variables (e.g., `protocol_var`, `codec_var`, metrics labels).
- **IP Management**: `add_ip_entry`/`remove_ip_entry` for dynamic entries.
- **Core Methods**: As described in "How It Works".
- **Main Block**: Creates Tk root, instantiates app, runs `mainloop`.
- **Error Handling**: Extensive `try-except` with `traceback` for debugging, `messagebox` for UI alerts.

Total lines: ~300, focused on clarity with comments (add more if needed).

## ⚠️ Troubleshooting
- **FFmpeg Not Found**: Check PATH; reinstall if needed.
- **Camera/Micro Errors**: Ensure permissions; test with simple OpenCV script.
- **Connection Fails**: Firewall/port issues; use `netstat` to check.
- **High CPU/Latency**: Lower resolution; close other apps.
- **Logs**: Inspect `metrics.log` and console for clues.
- **Crashes**: Run in debugger (e.g., VS Code) to trace exceptions.

## 📉 Limitations
- Sender-only; no built-in receiver.
- Simulated metrics (not real network feedback).
- No encryption (use VPN for security).
- Fixed settings (e.g., audio device); customize in code.
- Potential OS incompatibilities (audio/input).

## 🤝 Contributing
Fork the repo, make changes, and submit a PR! Suggestions: Add receiver mode, more codecs, real metrics via feedback loop, or Linux/macOS adaptations.

## 📜 License
MIT License - Feel free to use, modify, and share. See [LICENSE](LICENSE) file.

*Built with ❤️ in 2025. Open an issue for questions or feedback!*
