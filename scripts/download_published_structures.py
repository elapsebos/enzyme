#!/usr/bin/env python3
"""Download public author archives; validate checksums and extract structure inputs."""
import argparse
import csv
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import time
import zipfile
import requests

ROOT = Path(__file__).resolve().parents[1] / 'structures' / 'published'
SOURCES = {
    'jerves_2021_RESP_PET2': ('10.1021/acscatal.1c03700', 'https://api.figshare.com/v2/articles/16567410'),
    'burgin_2024_CGenFF_PET2': ('10.1038/s42004-024-01154-x', 'https://zenodo.org/api/records/10854763'),
    'berselli_2025_AM1BCC_PET4_PEF4': ('10.1021/acscatal.5c01263', 'https://zenodo.org/api/records/14697147'),
}
EXTENSIONS = {'.pdb', '.mol2', '.sdf', '.mol', '.gro', '.tpr', '.top', '.itp', '.prmtop',
              '.inpcrd', '.incpcrd', '.prm7', '.parm7', '.rst7', '.rst', '.crd', '.cor', '.coor', '.psf',
              '.rtf', '.prm', '.frcmod', '.off', '.lib', '.prepi', '.prep', '.xyz', '.mdp'}


def hash_file(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def download(url, path, size=None, md5=None):
    if path.exists():
        if (size is None or path.stat().st_size == size) and (md5 is None or hash_file(path, 'md5') == md5):
            return
        raise ValueError('Existing file has unexpected size/checksum; preserve and inspect: ' + str(path))
    part = path.with_suffix(path.suffix + '.part')
    for attempt in range(3):
        try:
            with requests.get(url, stream=True, timeout=(20, 90)) as response:
                response.raise_for_status()
                with part.open('wb') as output:
                    for block in response.iter_content(1024 * 1024):
                        output.write(block)
            if size is not None and part.stat().st_size != size:
                raise ValueError('Downloaded size mismatch')
            if md5 and hash_file(part, 'md5') != md5:
                raise ValueError('Downloaded checksum mismatch')
            if not zipfile.is_zipfile(part):
                raise ValueError('Download is not a valid ZIP archive')
            part.replace(path)
            return
        except (requests.RequestException, ValueError):
            if attempt == 2:
                raise
            time.sleep(1)


def extract_and_inventory(archive, target):
    rows = []
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            if member.is_dir():
                continue
            relative = PurePosixPath(member.filename)
            safe = not relative.is_absolute() and '..' not in relative.parts and ':' not in member.filename and '\\' not in member.filename
            selected = safe and '__MACOSX' not in relative.parts and not relative.name.startswith('._') and (
                relative.suffix.lower() in EXTENSIONS or relative.name.lower().startswith('readme'))
            row = dict(archive=archive.name, member=member.filename, bytes=member.file_size,
                       extracted=selected, sha256='')
            if selected:
                output = target.joinpath(*relative.parts)
                output.parent.mkdir(parents=True, exist_ok=True)
                data = z.read(member)
                if output.exists() and output.read_bytes() != data:
                    raise ValueError('Refusing to overwrite a modified extracted file: ' + str(output))
                output.write_bytes(data)
                row['sha256'] = hashlib.sha256(data).hexdigest()
            rows.append(row)
    return rows


def save_inventory(folder, rows):
    with (folder / 'archive_inventory.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['archive', 'member', 'bytes', 'extracted', 'sha256'])
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', choices=list(SOURCES) + ['all'], default='all')
    args = parser.parse_args()
    names = list(SOURCES) if args.source == 'all' else [args.source]
    for name in names:
        doi, url = SOURCES[name]
        folder = ROOT / name
        archive_folder = folder / 'archives'
        archive_folder.mkdir(parents=True, exist_ok=True)
        response = requests.get(url, timeout=40)
        response.raise_for_status()
        metadata = response.json()
        (folder / 'repository_metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
        rows, provenance = [], []
        for entry in metadata['files']:
            filename = entry.get('key', entry.get('name'))
            if not filename.lower().endswith('.zip'):
                continue
            link = entry['links']['self'] if 'links' in entry else entry['download_url']
            md5 = entry.get('computed_md5') or entry.get('checksum', '').removeprefix('md5:') or None
            archive = archive_folder / filename
            print('Downloading', name, filename, entry['size'], flush=True)
            download(link, archive, entry['size'], md5)
            rows.extend(extract_and_inventory(archive, folder / 'extracted'))
            provenance.append(dict(file=filename, url=link, bytes=archive.stat().st_size,
                                   md5=hash_file(archive, 'md5'), sha256=hash_file(archive),
                                   repository_md5=md5))
        save_inventory(folder, rows)
        (folder / 'provenance.json').write_text(json.dumps(dict(paper_doi=doi, metadata_url=url,
            downloaded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), archives=provenance), indent=2) + '\n')
        print('Verified:', name, 'extracted', sum(r['extracted'] for r in rows), 'of', len(rows), 'members', flush=True)


if __name__ == '__main__':
    main()
