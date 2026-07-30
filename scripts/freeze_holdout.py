#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

FROZEN_GLOBS = [
    'src/auditpoison/*.py',
    'prompts/auditor_system_v0.4.txt',
    'schema/evidence_bundle.schema.json',
    'pyproject.toml',
]

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def git(repo: Path, *args: str) -> str:
    p=subprocess.run(['git',*args],cwd=repo,text=True,capture_output=True,check=False)
    if p.returncode: raise SystemExit(p.stderr.strip() or f'git {" ".join(args)} failed')
    return p.stdout.strip()

def collect(repo: Path) -> list[Path]:
    paths=[]
    for pat in FROZEN_GLOBS:
        paths.extend(repo.glob(pat))
    return sorted({p.resolve() for p in paths if p.is_file()})

def build(repo: Path) -> dict:
    paths=collect(repo)
    if not paths: raise SystemExit('No frozen implementation files found.')
    files={p.relative_to(repo).as_posix():sha256_file(p) for p in paths}
    aggregate=hashlib.sha256()
    for rel,digest in sorted(files.items()): aggregate.update(rel.encode()+b'\0'+digest.encode()+b'\0')
    return {
      'schema_version':'1.0.0',
      'created_at_utc':datetime.now(timezone.utc).isoformat(),
      'git_commit':git(repo,'rev-parse','HEAD'),
      'git_branch':git(repo,'rev-parse','--abbrev-ref','HEAD'),
      'frozen_files':files,
      'implementation_sha256':aggregate.hexdigest(),
      'note':'Only security-critical implementation files are frozen; documentation-only commits may occur later.',
    }

def main():
    ap=argparse.ArgumentParser(description='Freeze EvidenceShield before blinded holdout evaluation.')
    ap.add_argument('--repo',default='.',help='AuditPoison repository')
    ap.add_argument('--output',default=None)
    ap.add_argument('--check-only',action='store_true')
    args=ap.parse_args(); repo=Path(args.repo).resolve()
    if not (repo/'.git').exists(): raise SystemExit(f'Not a Git repository: {repo}')
    tracked=git(repo,'status','--porcelain','--untracked-files=no')
    if tracked: raise SystemExit('Tracked working tree is not clean. Commit or restore changes before freezing.\n'+tracked)
    manifest=build(repo)
    print('EvidenceShield freeze check PASSED')
    print('git_commit:',manifest['git_commit'])
    print('implementation_sha256:',manifest['implementation_sha256'])
    print('frozen_files:',len(manifest['frozen_files']))
    if not args.check_only:
        if not args.output: raise SystemExit('--output is required unless --check-only is used')
        out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        print('Wrote',out)
if __name__=='__main__': main()
