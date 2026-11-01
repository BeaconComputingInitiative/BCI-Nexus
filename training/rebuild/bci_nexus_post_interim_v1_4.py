#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Nexus Guarded Post-Interim 10K Handoff v1.4.0
# Execute training if and only if predecessor PASS, integrity, approval and evaluation gates all pass.
import argparse, hashlib, json, math, os, random, sys, time
from pathlib import Path
HOME=Path.home(); DOC=HOME/'Documents'; SEAL='CJB-DEV-2026'
PRE=DOC/'BCI-Nexus-Interim-Continuation-v1.1.0'; LOG=DOC/'BCI-Nexus-Logs/continuation-20261101-011515.log'; STATUS=DOC/'BCI-Nexus-Logs/continuation-20261101-011515.status'
BASE=HOME/'BCI/models/Qwen3-1.7B'; HIST=HOME/'BCI/Qwen3-Training-v1.0.0/custom-v1.2/runs/fp32-r4/step-000125'
OUT=DOC/'BCI-Nexus-PostInterim-10K-v1.4.0'; NAMES=['bci_nexus_events_10k','bci_nexus_agent_actions_10k']
def fail(s): raise SystemExit('[BCI][BLOCK] '+s)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def verify(mdir):
 p=mdir/'SHA256SUMS'
 if not p.is_file():fail('Missing SHA256SUMS: '+str(p))
 for line in p.read_text().splitlines():
  if not line.strip():continue
  a=line.split(maxsplit=1)
  if len(a)!=2:fail('Malformed manifest '+str(p))
  dest=(mdir/a[1].lstrip('*')).resolve()
  if not dest.is_relative_to(mdir.resolve()) or not dest.is_file() or sha(dest)!=a[0]:fail('Hash mismatch '+str(dest))
def write_json(p,x):
 tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');tmp.replace(p)
def locate():
 dirs=[]
 for n in NAMES:
  matches=[x for x in DOC.glob('**/'+n) if x.is_dir() and (x/'train.jsonl').is_file()]
  if len(matches)!=1:fail('Expected exactly one extracted directory for '+n+'; found '+str(len(matches)))
  dirs.append(matches[0]);print('[BCI][DATA]',n,dirs[-1],flush=True)
 return dirs
def check_previous(wait):
 while True:
  state=PRE/'latest.json'
  if state.is_file():
   s=json.loads(state.read_text())
   if s.get('step')==100:
    checkpoint=(PRE/s['checkpoint']).resolve()
    if checkpoint.parent!=PRE.resolve():fail('Unsafe prior checkpoint path')
    for fn,digest in s.get('sha256',{}).items():
     fp=(checkpoint/fn).resolve()
     if not fp.is_relative_to(checkpoint) or not fp.is_file() or sha(fp)!=digest:fail('Prior checkpoint checksum invalid: '+str(fp))
    e=json.loads((checkpoint/'evaluation.json').read_text())
    if not math.isfinite(float(e['loss'])):fail('Nonfinite prior evaluation')
    if LOG.is_file() and '[BCI][PASS] Completed through step 100' in LOG.read_text(errors='replace'):
     if STATUS.exists():
      st=STATUS.read_text().lower()
      if not any(line.strip().replace(' ', '') in ('exitcode=0', 'exit_code=0', 'exit=0', 'rc=0', '0') for line in st.splitlines()):
       fail('Worker exit status uncertain/nonzero: '+st[:300])
     return checkpoint/'adapter',e
  if not wait:fail('Predecessor not conclusively finished with successful step 100')
  print('[BCI][WAIT] Interim training not yet confirmed complete; checking again in 60 seconds',flush=True)
  time.sleep(60)
def historical():
 for n in ('adapter_model.safetensors','adapter_config.json'):
  if not (HIST/n).is_file():fail('Step-125 reference missing: '+str(HIST/n))
 if sha(HIST/'adapter_model.safetensors')!='1bf1c3f36555032db080094cc159fa5588a1616fede2cc1512298f846546055e':fail('Step-125 weights changed from verified reference')
 if sha(HIST/'adapter_config.json')!='611926ab29d1abd138fbda4d2daa260806a035a3684d440ef4e39d2c3531bf6f':fail('Step-125 adapter config changed')
 return {'reference':str(HIST),'adapter_sha256':sha(HIST/'adapter_model.safetensors'),'role':'Source adapter for event stage; original checkpoint preserved'}
def scan_data(dirs):
 seen=set(); reports=[]
 for folder in dirs:
  verify(folder)
  report=json.loads((folder/'validation_report.json').read_text())
  if report.get('blocking_structural_checks_pass') is not True:fail('Structural check failed: '+str(folder))
  groups={}; counts={}; digests={}
  for split,total in (('train',9000),('eval',1000)):
   file=folder/(split+'.jsonl');digests[split]=sha(file);count=0
   for line in file.open():
    if not line.strip():continue
    rec=json.loads(line);count+=1
    key=rec.get('record_id');msgs=rec.get('messages');g=rec.get('source_group') or rec.get('metadata',{}).get('source_group')
    if not key or key in seen or not isinstance(msgs,list) or [m.get('role') for m in msgs]!=['system','user','assistant']:fail('Malformed or duplicate record '+str(key))
    if not g:fail('No source group for '+str(key))
    if g in groups and groups[g]!=split:fail('Train/eval group leakage '+str(g))
    groups[g]=split;seen.add(key)
   if count!=total:fail(f'{folder.name} {split} expected {total}, got {count}')
   counts[split]=count
  reports.append({'corpus':folder.name,'dir':str(folder),'count':counts,'sha256':digests,'review_pending':report.get('human_semantic_fact_review'),'tokenizer_pending':report.get('qwen3_tokenizer_validation')})
 return reports
def encode(tok,rec,seq):
 msgs=rec['messages']
 try:
  p=tok.apply_chat_template(msgs[:-1],tokenize=False,add_generation_prompt=True,enable_thinking=False)
  f=tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=False,enable_thinking=False)
  pi=tok(p,add_special_tokens=False).input_ids; fi=tok(f,add_special_tokens=False).input_ids
 except (ValueError,TypeError,KeyError):return None
 if len(pi)>=seq-8 or fi[:len(pi)]!=pi:return None
 fi=fi[:seq];lab=[-100]*len(pi)+fi[len(pi):]
 if sum(v!=-100 for v in lab[1:])<8:return None
 return fi,lab
def train_stage(folder,source,stage_no,args):
 import torch
 from peft import PeftModel
 from transformers import AutoModelForCausalLM,AutoTokenizer
 torch.set_num_threads(args.threads)
 try:torch.set_num_interop_threads(1)
 except RuntimeError:pass
 tok=AutoTokenizer.from_pretrained(BASE,local_files_only=True)
 dest=OUT/f'stage-{stage_no:02d}-{folder.name}';dest.mkdir(parents=True,exist_ok=True)
 inputs={'base':str(BASE),'source':str(source),'source_hash':sha(source/'adapter_model.safetensors'),'train_hash':sha(folder/'train.jsonl'),'eval_hash':sha(folder/'eval.jsonl'),'steps':args.steps,'seq':args.seq,'lr':args.lr,'eval_count':args.eval_count,'save_every':args.save_every,'seal':SEAL}
 conf=dest/'config.json';state=dest/'latest.json'
 if conf.exists() and json.loads(conf.read_text())!=inputs:fail('Stage configuration changed '+str(dest))
 if not conf.exists():write_json(conf,inputs)
 def read_encoded(split):
  entries=[];discarded=0
  for line in (folder/(split+'.jsonl')).open():
   if not line.strip():continue
   encoded=encode(tok,json.loads(line),args.seq)
   if encoded is None:discarded+=1;continue
   entries.append(encoded)
  return entries,discarded
 train,train_skip=read_encoded('train');val,val_skip=read_encoded('eval')
 print(f'[BCI][TOKENIZER] stage={stage_no} usable_train={len(train)} skipped_train={train_skip} usable_eval={len(val)} skipped_eval={val_skip}',flush=True)
 if len(train)<args.steps or len(val)<args.eval_count:fail('Insufficient tokenizable examples for requested steps and eval')
 if len(train)<int(0.8*9000) or len(val)<int(0.8*1000):fail('Tokenizer retained fewer than 80% of examples; review length configuration')
 # The two corpora are nominally 10K but tokenization can discard long records; record all discarded counts.
 write_json(dest/'tokenization.json',{'train_usable':len(train),'train_skipped':train_skip,'eval_usable':len(val),'eval_skipped':val_skip,'seq':args.seq})
 rr=random.Random(2026+stage_no);rr.shuffle(train)
 ve=random.Random(3000+stage_no).sample(val,args.eval_count)
 step=0; adapter=source;checkpoint=None
 if state.exists():
  saved=json.loads(state.read_text());step=saved['step'];checkpoint=(dest/saved['checkpoint']).resolve()
  if checkpoint.parent!=dest.resolve():fail('Unsafe resume checkpoint path')
  if saved.get('source_hash')!=inputs['source_hash']:fail('Resumed stage source adapter changed')
  for name,digest in saved['sha256'].items():
   p=(checkpoint/name).resolve()
   if not p.is_relative_to(checkpoint) or not p.is_file() or sha(p)!=digest:fail('Stage checkpoint corrupt '+str(p))
  adapter=checkpoint/'adapter'
 if step>=args.steps:
  if step!=args.steps:fail('Saved step exceeds requested step count')
  return adapter
 torch.manual_seed(2026+stage_no)
 base=AutoModelForCausalLM.from_pretrained(BASE,local_files_only=True,dtype=torch.float32,low_cpu_mem_usage=True,attn_implementation='sdpa')
 base.config.use_cache=False
 model=PeftModel.from_pretrained(base,adapter,is_trainable=True)
 parameters=[p for p in model.parameters() if p.requires_grad]
 if not parameters:fail('No trainable LoRA parameters')
 opt=torch.optim.AdamW(parameters,lr=args.lr)
 if step:opt.load_state_dict(torch.load(checkpoint/'optimizer.pt',map_location='cpu',weights_only=True))
 def loss_eval():
  model.eval();n=0;s=0.0
  with torch.inference_mode():
   for ids,labs in ve:
    x=torch.tensor([ids]);y=torch.tensor([labs]);c=sum(z!=-100 for z in labs[1:]);v=float(model(input_ids=x,attention_mask=torch.ones_like(x),labels=y).loss.item())
    if not math.isfinite(v):fail('Nonfinite evaluation loss')
    s+=v*c;n+=c
  return {'loss':s/n,'tokens':n,'examples':len(ve)}
 if step==0:
  base_score=loss_eval();write_json(dest/'baseline-evaluation.json',base_score);print('[BCI][EVAL] baseline',base_score,flush=True)
 for i in range(step,args.steps):
  ids,labs=train[i];x=torch.tensor([ids]);y=torch.tensor([labs]);model.train();opt.zero_grad(set_to_none=True)
  loss=model(input_ids=x,attention_mask=torch.ones_like(x),labels=y).loss
  if not bool(torch.isfinite(loss).item()):fail('Nonfinite training loss')
  value=float(loss.item());loss.backward();torch.nn.utils.clip_grad_norm_(parameters,1.0);opt.step()
  print(f'[BCI][TRAIN] stage={stage_no} step={i+1}/{args.steps} loss={value:.6f}',flush=True)
  if (i+1)%args.save_every==0 or i+1==args.steps:
   score=loss_eval();print(f'[BCI][EVAL] stage={stage_no} step={i+1} {score}',flush=True)
   stage=dest/f'.stage-{i+1:06d}';final=dest/f'step-{i+1:06d}'
   if stage.exists() or final.exists():fail('Checkpoint destination collision '+str(final))
   stage.mkdir();model.save_pretrained(stage/'adapter');torch.save(opt.state_dict(),stage/'optimizer.pt');write_json(stage/'evaluation.json',score)
   hashes={str(p.relative_to(stage)):sha(p) for p in stage.rglob('*') if p.is_file()};stage.rename(final)
   write_json(state,{'step':i+1,'checkpoint':final.name,'sha256':hashes,'source_hash':inputs['source_hash']})
   print('[BCI][CHECKPOINT]',final,flush=True)
 final_score=loss_eval()
 # A regression relative to the same corpus' baseline requires human evaluation rather than blind transition.
 initial=json.loads((dest/'baseline-evaluation.json').read_text())
 if final_score['loss']>initial['loss']*1.05:fail('Evaluation regressed >5% from stage baseline; stop before next stage')
 print(f'[BCI][PASS] Stage {stage_no} finished; baseline={initial["loss"]:.6f} final={final_score["loss"]:.6f}',flush=True)
 return dest/f'step-{args.steps:06d}'/'adapter'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--wait',action='store_true');ap.add_argument('--steps',type=int,default=250);ap.add_argument('--seq',type=int,default=512);ap.add_argument('--eval-count',type=int,default=16);ap.add_argument('--save-every',type=int,default=25);ap.add_argument('--threads',type=int,default=4);ap.add_argument('--lr',type=float,default=2e-5);args=ap.parse_args()
 if args.steps<1 or args.seq<128 or args.seq>1024 or args.eval_count<4 or args.save_every<1:fail('Invalid configuration')
 if not (BASE/'config.json').is_file():fail('Qwen3 base not present')
 dirs=locate();reports=scan_data(dirs)
 OUT.mkdir(parents=True,exist_ok=True)
 write_json(OUT/'dataset-audit.json',{'seal':SEAL,'dataset_reports':reports,'automatic_structure_checks':'PASS','semantic_expert_review':'PENDING'})
 print('[BCI][DATA] Structural checks passed. Full expert review is pending.',flush=True)
 if os.environ.get('BCI_10K_REVIEW_APPROVED')!='YES':fail('Datasets report human semantic review PENDING. Set BCI_10K_REVIEW_APPROVED=YES only after reviewing and approving the corpora.')
 interim_adapter,evaluation=check_previous(args.wait)
 hist=historical(); source=HIST
 write_json(OUT/'step-125-reference.json',{'historical':hist,'interim_step100_eval':evaluation,'interim_adapter_sha256':sha(interim_adapter/'adapter_model.safetensors'),'initial_adapter':str(source),'lineage':'custom-v1.2 step125 -> Event Intelligence -> Agent Actions'})
 print('[BCI][BALANCE] Interim step100 verified. Training starts from custom-v1.2 step125; original reference preserved.',flush=True)
 for ix,folder in enumerate(dirs,1):source=train_stage(folder,source,ix,args)
 write_json(OUT/'complete.json',{'status':'PASS','seal':SEAL,'final_adapter':str(source),'sha256':sha(source/'adapter_model.safetensors')})
 print('[BCI][PASS] Both post-interim training stages completed',flush=True)
if __name__=='__main__':main()
