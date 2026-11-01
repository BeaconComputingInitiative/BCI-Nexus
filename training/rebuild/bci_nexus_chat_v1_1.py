#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Nexus Interactive Chat v1.1.0
# Gate: Launch if and only if no competing training process exists and checkpoint integrity passes.
import hashlib
import json
import subprocess
from pathlib import Path

HOME = Path.home()
BASE = HOME / 'BCI/models/Qwen3-1.7B'
ROOT = HOME / 'Documents/BCI-Nexus-PostInterim-10K-v1.4.0'
FALLBACK = HOME / 'BCI/Qwen3-Training-v1.0.0/custom-v1.2/runs/fp32-r4/step-000125'

def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()

def training_active():
    proc = subprocess.run(['ps', '-eo', 'args='], capture_output=True, text=True, check=True)
    return any('bci_nexus_post_interim_v1_4.py' in line and 'python' in line for line in proc.stdout.splitlines())

def select_checkpoint():
    for stage in sorted(ROOT.glob('stage-*'), reverse=True):
        latest = stage / 'latest.json'
        if not latest.is_file():
            continue
        state = json.loads(latest.read_text(encoding='utf-8'))
        checkpoint = (stage / str(state.get('checkpoint', ''))).resolve()
        if checkpoint.parent != stage.resolve():
            continue
        files = state.get('sha256', {})
        if not files or not all((checkpoint / name).is_file() and sha256(checkpoint / name) == expected for name, expected in files.items()):
            print(f'[BCI][WARN] Ignoring invalid checkpoint: {checkpoint}')
            continue
        adapter = checkpoint / 'adapter'
        if (adapter / 'adapter_config.json').is_file() and (adapter / 'adapter_model.safetensors').is_file():
            return adapter, f'{stage.name}/step-{state.get("step")}'
    if (FALLBACK / 'adapter_config.json').is_file() and (FALLBACK / 'adapter_model.safetensors').is_file():
        if sha256(FALLBACK / 'adapter_model.safetensors') != '1bf1c3f36555032db080094cc159fa5588a1616fede2cc1512298f846546055e':
            raise RuntimeError('Fallback Step-125 adapter hash mismatch')
        return FALLBACK, 'custom-v1.2/step-125'
    raise RuntimeError('No valid adapter available')

def main():
    if training_active():
        print('[BCI][BLOCK] Training is still active; avoid loading a second FP32 model.')
        return
    if not (BASE / 'config.json').is_file():
        print(f'[BCI][BLOCK] Missing base model: {BASE}')
        return
    adapter, label = select_checkpoint()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    torch.set_num_threads(4)
    print(f'[BCI][LOAD] Checkpoint: {label}')
    print(f'[BCI][LOAD] Adapter: {adapter}')
    tokenizer = AutoTokenizer.from_pretrained(BASE, local_files_only=True)
    base = AutoModelForCausalLM.from_pretrained(BASE, local_files_only=True,
                                                dtype=torch.float32,
                                                low_cpu_mem_usage=True,
                                                attn_implementation='sdpa')
    model = PeftModel.from_pretrained(base, adapter, is_trainable=False)
    model.eval()
    model.generation_config.do_sample = False
    model.generation_config.temperature = None
    model.generation_config.top_p = None
    model.generation_config.top_k = None
    history = []
    print('[BCI][READY] Type /exit to quit, /clear to reset conversation.')
    while True:
        try:
            prompt = input('YOU > ').strip()
        except (KeyboardInterrupt, EOFError):
            print('\n[BCI] Session ended.')
            return
        if prompt.lower() in {'/exit', '/quit'}:
            return
        if prompt.lower() == '/clear':
            history.clear()
            print('[BCI] History cleared.')
            continue
        if not prompt:
            continue
        messages = [{'role': 'system', 'content': 'You are BCI Nexus, a precise engineering assistant for Beacon Computing Initiative. Never claim to have run commands without tool evidence.'}, *history[-8:], {'role': 'user', 'content': prompt}]
        encoded = tokenizer.apply_chat_template(messages, tokenize=True,
                    add_generation_prompt=True, enable_thinking=False, return_tensors='pt')
        if encoded.shape[-1] > 3072:
            print('[BCI][WARN] Context too long; clearing prior turns for this response.')
            messages = [messages[0], messages[-1]]
            encoded = tokenizer.apply_chat_template(messages, tokenize=True,
                        add_generation_prompt=True, enable_thinking=False, return_tensors='pt')
        with torch.inference_mode():
            result = model.generate(input_ids=encoded, max_new_tokens=256,
                        do_sample=False, pad_token_id=tokenizer.eos_token_id)
        reply = tokenizer.decode(result[0][encoded.shape[-1]:], skip_special_tokens=True).strip()
        print(f'\nNEXUS > {reply}\n')
        history.extend([{'role': 'user', 'content': prompt}, {'role': 'assistant', 'content': reply}])

if __name__ == '__main__':
    main()
