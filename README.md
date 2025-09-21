# vitool

`vitool` is a Python toolkit that provides utilities for working with remote files, including downloading, caching, and extracting archives.

---

## `rfile.py` — File Downloading and Extraction Utilities

`vitool/rfile.py` is a Python utility module for **downloading, caching and extracting remote files**.
It supports plain HTTP/HTTPS, Yandex Disk shared links, and automatic extraction of archives ( **.zip**, **.tar.***, etc.).

---

### ✨ Features

- ✅ Download files from URLs with progress bar.
- ✅ Automatic extraction of **.zip** and **.tar.*** archives
- ✅ Convenient handling of existing files (skip or redownload)
- ✅ Verbose logging with optional quiet mode
- ✅ Cookie and proxy support via **requests.Session**

---

## 📦 Installation

```bash
pip install vitool
```

---

### 📖 Example Usage

#### 📦 Functions

`download(url, path="", extract_to=True, redownload=False, quiet=False, https=None)`
Download a file from `url` to local `path`.
- If `extract_to=True`, automatically extracts archives.
- If `extract_to=False`, just downloads the file.
- If a path is provided in `extract_to`, extracts there.

**Returns:** Path to the downloaded or extracted file/directory.

```python
from vitool import rfile

# Download and extract an archive
rfile.download( "https://example.com/data.zip", path="./downloads" )
```

---

#### 📦 Classes

`Extract(file_path, extract_path=None, reextract=False, quiet=False)`
Utility for extracting archives.
- `file_path`: Path to the archive file.
- `extract_path`: Directory to extract into; defaults to same directory.
- `reextract`: Whether to overwrite existing files.
- `quiet`: Suppress progress / info output.
Supports `.zip` and `.tar.*` formats.

---

`Https(user_agent=None, use_cookies=True, proxy=None, https=None)`
Wrapper around `requests.Session` with extras.
- `user_agent`: Custom User-Agent string; if None, defaults to Firefox.
- `use_cookies`: Whether to use persistent cookies stored on disk.
- `proxy`: Optional proxy server (applies to both HTTP and HTTPS).
- `https`: If another Https instance is provided, clone its session.
If `https` is given, the session and cookie settings are copied.
Otherwise, a new requests.Session is created.

---

## 🚀 Running Tests

Run all unit tests with verbose output:

```bash
python -m unittest -v
```

---

