#!/usr/bin/env python3
import tarfile
import zipfile
import io
from pathlib import Path

TAR_FILES = [
    Path("raw/zenodo/CRBC_BGC_part_1.tar.gz"),
    Path("raw/zenodo/CRBC_BGC_part_2.tar.gz"),
]
GENOME_LIST = Path("results/05_ranking/hserlactone_genomes.txt")
OUT_DIR = Path("processed/region_gbks_hserlactone")
OUT_DIR.mkdir(parents=True, exist_ok=True)

wanted = {line.strip() for line in GENOME_LIST.read_text().splitlines() if line.strip()}
print("wanted genomes:", len(wanted))

found = 0
saved = 0
for tar_path in TAR_FILES:
    if not tar_path.exists():
        print("missing", tar_path)
        continue
    print("opening", tar_path)
    with tarfile.open(tar_path, "r:gz") as tar:
        for m in tar.getmembers():
            if not m.isfile() or not m.name.endswith(".zip"):
                continue
            genome_id = Path(m.name).stem
            if genome_id not in wanted:
                continue
            found += 1
            zf = tar.extractfile(m)
            if zf is None:
                continue
            with zipfile.ZipFile(io.BytesIO(zf.read())) as z:
                for n in z.namelist():
                    if ".region" in n and n.endswith(".gbk"):
                        out = OUT_DIR / Path(n).name
                        if not out.exists():
                            out.write_bytes(z.read(n))
                            saved += 1
            if found % 20 == 0:
                print("genomes found", found, "gbks saved", saved)

print("done. genomes found", found, "region gbks saved", saved)
print(OUT_DIR)
