"""Download the pinned official LibreDWG release, validating SHA256 before use."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import shutil
from pathlib import Path
import time
import sys
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SHA256 = "1ad7e15344d20b3426c3435b078d82fb84b35062815946b2cca9c5fc9810fea8"
SIZE = 12084779
URL = "https://api.github.com/repos/LibreDWG/libredwg/releases/assets/459621479"
HEADERS = {"Accept": "application/octet-stream", "User-Agent": "nfc-coil-calculator-build"}


def download(url=URL, size=SIZE, expected=SHA256, source=False):
    dest = ROOT / ("dist/sources/libredwg-0.14.tar.xz" if source else "tools/libredwg-official.zip")
    dest.parent.mkdir(parents=True, exist_ok=True)
    parts = ROOT / "tools" / ("source-parts" if source else "download-parts")
    parts.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=HEADERS, method="HEAD")
    with urllib.request.urlopen(request, timeout=45) as response:
        resolved = response.geturl()
    count = 8
    chunk = (size + count - 1) // count

    def fetch(index):
        start, end = index * chunk, min(size - 1, (index + 1) * chunk - 1)
        part = parts / f"part-{index:02d}.bin"
        if part.exists() and part.stat().st_size == end - start + 1:
            return index
        for attempt in range(3):
            try:
                request = urllib.request.Request(resolved, headers={**HEADERS, "Range": f"bytes={start}-{end}"})
                with urllib.request.urlopen(request, timeout=90) as response:
                    if response.status != 206:
                        raise RuntimeError(f"Expected byte range response, got {response.status}")
                    if response.headers.get("Content-Range", "").split('/')[0] != f"bytes {start}-{end}":
                        raise RuntimeError("Unexpected byte range")
                    data = response.read()
                if len(data) != end - start + 1:
                    raise RuntimeError("Incomplete byte range")
                part.write_bytes(data)
                return index
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2)

    with ThreadPoolExecutor(max_workers=count) as pool:
        futures = [pool.submit(fetch, index) for index in range(count)]
        for future in as_completed(futures):
            print(f"Official download part {future.result()+1}/{count} complete", flush=True)
    with dest.open("wb") as output:
        for index in range(count):
            output.write((parts / f"part-{index:02d}.bin").read_bytes())
    actual = hashlib.sha256(dest.read_bytes()).hexdigest()
    if actual != expected:
        raise RuntimeError("Official archive SHA256 mismatch")
    if not source:
        with zipfile.ZipFile(dest) as archive:
            archive.extractall(ROOT / "tools" / "libredwg")
        shutil.copy2(ROOT / "tools/libredwg/examples/dwgadd.exe", ROOT / "tools/libredwg/dwgadd.exe")
    print("Official LibreDWG SHA256 verified" + (" (source)" if source else " and archive extracted"), flush=True)


if __name__ == "__main__":
    if "--source" in sys.argv:
        request = urllib.request.Request("https://api.github.com/repos/LibreDWG/libredwg/releases/latest",
                                         headers={"User-Agent": HEADERS["User-Agent"]})
        with urllib.request.urlopen(request, timeout=45) as response:
            release = json.load(response)
        asset = next(a for a in release["assets"] if a["name"] == "libredwg-0.14.tar.xz")
        download(asset["url"], asset["size"],
                 "62ebb73b984f865960f20ed26619ea5f8789d5e3fd088fa40a2598384da81275", True)
    else:
        download()
