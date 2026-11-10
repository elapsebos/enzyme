#!/usr/bin/env python3
"""Inventory downloaded author archives without modifying author files."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import zipfile

from download_published_structures import ROOT, extract_and_inventory, hash_file, save_inventory


def flags(path):
    text = path.read_text(errors='replace')
    result = {}
    for match in re.finditer(r'%FLAG\s+(\S+)\s*\n%FORMAT\(([^)]+)\)\s*\n(.*?)(?=%FLAG|\Z)', text, re.S):
        name, fmt, body = match.groups()
        if name in ('ATOM_NAME', 'RESIDUE_LABEL'):
            result[name] = [line[i:i+4].strip() for line in body.splitlines() if not line.startswith('%')
                            for i in range(0, len(line), 4) if line[i:i+4].strip()]
        elif name in ('POINTERS', 'RESIDUE_POINTER'):
            result[name] = [int(n) for n in body.split() if re.fullmatch(r'-?\d+', n)]
    return result


def main():
    github = ROOT / 'dipede_2026_RESP_PET4'
    if (github / 'archives/repository_snapshot.zip').exists():
        commit = json.loads((github / 'github_commit.json').read_text(encoding='utf-8-sig'))
        tree = json.loads((github / 'github_tree.json').read_text(encoding='utf-8-sig'))
        if tree['sha'] != commit['commit']['tree']['sha']:
            raise ValueError('Git tree does not match archived commit')
        blobs = {item['path']: item['sha'] for item in tree['tree'] if item['type'] == 'blob'}
        verified = 0
        with zipfile.ZipFile(github / 'archives/repository_snapshot.zip') as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                name = member.filename.split('/', 1)[1]
                data = archive.read(member)
                blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                if blob != blobs[name]:
                    raise ValueError('Git blob mismatch: ' + name)
                verified += 1
                if name == 'PETase-cryst-vs-amor.zip':
                    target = github / 'archives/PETase-cryst-vs-amor.zip'
                    if target.exists() and target.read_bytes() != data:
                        raise ValueError('Author ZIP changed locally')
                    target.write_bytes(data)
        files = [dict(file=p.name, bytes=p.stat().st_size, sha256=hash_file(p))
                 for p in (github / 'archives').glob('*.zip')]
        (github / 'provenance.json').write_text(json.dumps(dict(
            paper_doi='10.1021/acs.jpclett.6c00308',
            repository='https://github.com/fcolizzi/PETase_Cryst-vs-Amor', commit=commit['sha'],
            archive_url='https://codeload.github.com/fcolizzi/PETase_Cryst-vs-Amor/zip/' + commit['sha'],
            git_blobs_verified=verified, archives=files), indent=2) + '\n')
    summary, structures = [], []
    for folder in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        rows = []
        for archive in sorted((folder / 'archives').glob('*.zip')):
            rows.extend(extract_and_inventory(archive, folder / 'extracted'))
        if not rows:
            continue
        save_inventory(folder, rows)
        chosen = [r for r in rows if r['extracted']]
        counts = collections.Counter(Path(r['member']).suffix.lower() for r in chosen)
        summary.append(dict(source=folder.name, archives=len(list((folder / 'archives').glob('*.zip'))),
                            selected_files=len(chosen), types=dict(counts)))
        for top in (folder / 'extracted').rglob('*.prmtop'):
            data = flags(top)
            pointers = data.get('POINTERS', [])
            structures.append(dict(source=folder.name, file=str(top.relative_to(ROOT)),
                                   atoms=pointers[0] if pointers else None,
                                   residues=len(data.get('RESIDUE_LABEL', [])),
                                   residue_labels=dict(collections.Counter(data.get('RESIDUE_LABEL', [])))))
        for gro in (folder / 'extracted').rglob('*.gro'):
            with gro.open() as stream:
                title = stream.readline().strip()
                n = int(stream.readline())
                labels = collections.Counter(stream.readline()[5:10].strip() for _ in range(n))
            structures.append(dict(source=folder.name, file=str(gro.relative_to(ROOT)),
                                   atoms=n, title=title, atom_residue_labels=dict(labels)))
    (ROOT / 'download_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (ROOT / 'structure_contents.json').write_text(json.dumps(structures, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    seen = set()
    for row in structures:
        if row['source'] not in seen:
            print('Example:', row['source'], Path(row['file']).name, row['atoms'])
            seen.add(row['source'])


if __name__ == '__main__':
    main()
