#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Nexus Stage-3 Agentic Engineering & Execution Handoff v1.0
# Run if and only if source checkpoint, dataset, review and isolation gates pass.
import argparse, hashlib, importlib.util, json, math, os, shutil, subprocess, sys, zipfile
from pathlib import Path

HOME=Path.home(); DOC=HOME/'Documents'; SEAL='CJB-DEV-2026'
NAME='BCI-Nexus-Agentic-Engineering-Execution-10K-v3.0.0.zip'
ZIP_HASH='18b0563e6cdce3cefc7a464a47dcb1bbb4c1e20672848e6ec7300ab83e539802'
PRE=DOC/'BCI-Nexus-PostInterim-10K-v1.4.0'
S2=PRE/'stage-02-bci_nexus_agent_actions_10k'/'step-000250'
SOURCE=S2/'adapter'
SOURCE_HASH='20a0fe9f3c868e08597d3b3a3bb89caa9ea6980cf213040df4dab34db7f817b2'
DATA=DOC/'BCI-Nexus-Agentic-Engineering-Execution-10K-v3.0.0'
OUT=DOC/'BCI-Nexus-Stage3-Agentic-Engineering-v1.0.0'
STAGE=OUT/'stage-03-bci_nexus_agentic_engineering_execution_10k'
CONTROLLER=DOC/'bci_nexus_post_interim_v1_4.py'

def fail(msg): raise SystemExit('[BCI][BLOCK] '+msg)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');tmp.replace(path)
def source_gate():
    complete=PRE/'complete.json'; latest=S2.parent/'latest.json'
    if not complete.is_file() or not latest.is_file(): fail('Stage-2 completion or latest.json missing')
    a=json.loads(complete.read_text()); s=json.loads(latest.read_text())
    if (a.get('status')!='PASS' or a.get('seal')!=SEAL or
        Path(a.get('final_adapter','')).resolve()!=SOURCE.resolve() or
        a.get('sha256')!=SOURCE_HASH or s.get('step')!=250 or
        s.get('checkpoint')!='step-000250'): fail('Stage-2 completion lineage invalid')
    if not (SOURCE/'adapter_model.safetensors').is_file() or sha(SOURCE/'adapter_model.safetensors')!=SOURCE_HASH:
        fail('Stage-2 adapter digest mismatch')
    if not s.get('sha256'): fail('Stage-2 checkpoint digest map missing')
    for name,digest in s['sha256'].items():
        p=(S2/name).resolve()
        if not p.is_relative_to(S2.resolve()) or not p.is_file() or sha(p)!=digest:
            fail('Stage-2 checkpoint invalid: '+name)
    print('[BCI][PASS] Stage-2 Step-250 checkpoint verified',flush=True)
def archive_gate():
    paths=[HOME/'Downloads'/NAME,DOC/NAME,HOME/'Desktop'/NAME]
    if (HOME/'Downloads').is_dir(): paths.extend((HOME/'Downloads').rglob(NAME))
    if DOC.is_dir(): paths.extend(DOC.rglob(NAME))
    archives=sorted({p.resolve() for p in paths if p.is_file()})
    if not archives: fail('Dataset ZIP missing from Downloads/Documents/Desktop: '+NAME)
    valid=[p for p in archives if sha(p)==ZIP_HASH]
    if not valid: fail('Dataset archive SHA-256 mismatch')
    print('[BCI][PASS] Dataset ZIP SHA-256 verified: '+str(valid[0]),flush=True)
    return valid[0]
def extract(archive):
    marker=DATA/'.bci-archive-sha256'
    if marker.is_file() and marker.read_text().strip()==ZIP_HASH:return
    if DATA.exists():fail('Extraction destination exists without verified marker: '+str(DATA))
    import tempfile
    with tempfile.TemporaryDirectory(prefix='.bci-stage3-',dir=DOC) as d:
        dest=Path(d)/'payload';dest.mkdir()
        with zipfile.ZipFile(archive) as z:
            infos=z.infolist()
            if not infos or sum(i.file_size for i in infos)>1073741824:fail('ZIP empty or too large')
            for item in infos:
                target=(dest/item.filename).resolve()
                kind=(item.external_attr>>16)&0o170000
                if (Path(item.filename).is_absolute() or not target.is_relative_to(dest.resolve()) or
                    '\\' in item.filename or kind==0o120000): fail('Unsafe ZIP entry')
            z.extractall(dest)
        (dest/marker.name).write_text(ZIP_HASH+'\n')
        dest.rename(DATA)
    print('[BCI][PASS] Dataset extracted: '+str(DATA),flush=True)
def load_data():
    folders=[p.parent for p in DATA.rglob('train.jsonl')
             if all((p.parent/n).is_file() for n in ('eval.jsonl','SHA256SUMS','validation_report.json'))]
    if len(folders)!=1:fail('Expected one corpus with train/eval/validation/SHA256SUMS; found '+str(len(folders)))
    if not CONTROLLER.is_file():fail('Existing training controller missing: '+str(CONTROLLER))
    spec=importlib.util.spec_from_file_location('bci_stage3_controller',CONTROLLER)
    c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    reports=c.scan_data(folders)
    write_json(OUT/'dataset-audit.json',{'seal':SEAL,'source_adapter':str(SOURCE),
               'source_sha256':SOURCE_HASH,'archive_sha256':ZIP_HASH,
               'reports':reports,'semantic_review':'REQUIRES_EXPLICIT_APPROVAL'})
    print('[BCI][PASS] Stage-3 dataset structural validation: 9000 train / 1000 eval',flush=True)
    print('[BCI][DATA] '+str(folders[0]),flush=True)
    return folders[0],c
def isolation_gate():
    ps=subprocess.run(['ps','-eo','pid=,args='],capture_output=True,text=True,check=True)
    for line in ps.stdout.splitlines():
        parts=line.strip().split(maxsplit=1)
        if len(parts)!=2:continue
        try: pid=int(parts[0])
        except ValueError:continue
        if pid==os.getpid():continue
        args=parts[1]
        if 'python' in args and ('/BCI/Nexus/chat.py' in args or 'bci_nexus_post_interim_v1_4.py' in args):
            fail('Competing Nexus process active: PID '+str(pid))
def stage3():
    if os.environ.get('BCI_STAGE3_REVIEW_APPROVED')!='YES':
        fail('Stage-3 semantic review not approved; set BCI_STAGE3_REVIEW_APPROVED=YES only after review')
    isolation_gate(); source_gate(); zipfile_path=archive_gate();extract(zipfile_path)
    folder,c=load_data();c.OUT=OUT
    a=argparse.Namespace(steps=250,seq=512,eval_count=16,save_every=25,threads=4,lr=2e-5)
    print('[BCI][START] Stage 3 from verified Stage-2 adapter',flush=True)
    adapter=c.train_stage(folder,SOURCE,3,a)
    checkpoint=STAGE/'step-000250'
    if adapter.resolve()!=(checkpoint/'adapter').resolve():fail('Unexpected final adapter')
    before=json.loads((STAGE/'baseline-evaluation.json').read_text())
    after=json.loads((checkpoint/'evaluation.json').read_text())
    if not (math.isfinite(float(before['loss'])) and math.isfinite(float(after['loss']))):fail('Nonfinite loss')
    if after['loss']>before['loss']*1.05:fail('Evaluation regressed more than 5%')
    digest=sha(adapter/'adapter_model.safetensors')
    write_json(OUT/'complete.json',{'status':'PASS','seal':SEAL,'stage':3,'source':str(SOURCE),
        'source_sha256':SOURCE_HASH,'final_adapter':str(adapter),'sha256':digest,
        'baseline_loss':before['loss'],'final_loss':after['loss'],
        'optimizer_steps':250,'note':'250 steps sample 250 shuffled examples, not all 9000.'})
    print('[BCI][PASS] Stage 3 complete',flush=True)
    print('[BCI][SHA256] '+digest,flush=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','train','status'])
    action=parser.parse_args().action
    if action=='status':
        p=OUT/'complete.json';s=STAGE/'latest.json'
        if p.is_file():print(p.read_text())
        elif s.is_file():print('[BCI][PROGRESS]',json.loads(s.read_text()).get('step'),'/250')
        else:print('[BCI][INFO] No Stage-3 checkpoint yet')
    elif action=='prepare':
        source_gate();extract(archive_gate());load_data()
    else:stage3()
if __name__=='__main__':main()
