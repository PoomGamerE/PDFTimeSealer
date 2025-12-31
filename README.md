# 🛡PDFTimeSealer

**PDFTimeSealer** is a cross-platform, portable desktop application designed to apply RFC 3161 trusted timestamps to PDF documents. It ensures long-term validation and integrity of your files without relying on external servers for file storage.

<p align="center">
  <img src="app_icon.ico" width="128" alt="PDFTimeSealer Icon">
</p>

## ✨ Key Features

* **Cross-Platform:** Runs seamlessly on Windows, macOS, and Linux.
* **Portable:** No installation required. Just download and run.
* **Batch Processing:** Drag and drop multiple PDF files for bulk timestamping.
* **Smart Repair:** Automatically repairs corrupted PDF structures (e.g., bank statements) before timestamping.
* **RFC 3161 Compliant:** Supports standard timestamping servers (Default: DigiCert).
* **Privacy Focused:** Files are processed locally on your machine. No documents are uploaded to any cloud server.

## 🚀 Installation & Usage

### For Windows Users
1. Download `PDFTimeSealer-Windows.exe` from the [Releases Page](../../releases).
2. Double-click to run (No admin rights required).
3. Drag and drop your PDFs and click **Start Timestamping**.

### For macOS Users
1. Download `PDFTimeSealer-macOS` from the [Releases Page](../../releases).
2. Right-click the file and select **Open** (required for the first run due to Apple security).
3. Provide permissions if requested.

### For Linux Users
1. Download `PDFTimeSealer-Linux` from the [Releases Page](../../releases).
2. Open terminal and make the file executable:
   ```bash
   chmod +x PDFTimeSealer-Linux
   ./PDFTimeSealer-Linux

```

## 🛠️ Development

If you want to run from source or build it yourself:

### Prerequisites

* Python 3.10+
* `pip`

### Setup

1. Clone the repository:
```bash
git clone [https://github.com/PoomGamerE/PDFTimeSealer.git](https://github.com/PoomGamerE/PDFTimeSealer.git)
cd PDFTimeSealer

```


2. Install dependencies:
```bash
pip install -r requirements.txt

```


3. Run the application:
```bash
python main.py

```



## 📦 Building from Source

To create a standalone executable for your current OS:

```bash
python build.py

```

## 📜 License

This project is licensed under the **MIT License**. Feel free to use, modify, and distribute.
