#!/usr/bin/env python3
# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Nexus Stage-3 Compatible Dataset Handoff v1.1
# Safety gate: train if and only if source, integrity, schema, tokenizer, approval and isolation checks pass.
"""Preserve the Stage-3 source archive; project simulated tool episodes into 3-role examples.

This is a compatibility projection, not expert semantic validation or independent evaluation.
Training uses the existing v1.4 controller and Stage-2 adapter without modifying either.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

SEAL = "CJB-DEV-2026"
HOME = Path.home()
DOC = HOME / "Documents"
VERSION = "1.1.0"
ORIGINAL = DOC / "BCI-Nexus-Stage3-Launcher-v1.0.py"
CONTROLLER = DOC / "bci_nexus_post_interim_v1_4.py"
EXPECTED_LAUNCHER = "6a0509fe37e8eab9044a3822432d1f1e4f419b35bd1e573239b5149024de4023"
EXPECTED_CONTROLLER = "b1482cb4783c8250a5788d70cee9ead702efa054ce373d187074fe41eb5c0ed4"
ZIP_HASH = "18b0563e6cdce3cefc7a464a47dcb1bbb4c1e20672848e6ec7300ab83e539802"
OUT = DOC / "BCI-Nexus-Stage3-Agentic-Engineering-v1.0.0"
DATA = OUT / "projected-dataset" / "bci_nexus_agentic_engineering_execution_10k"
STAGE = OUT / "stage-03-bci_nexus_agentic_engineering_execution_10k"
BASE = HOME / "BCI/models/Qwen3-1.7B"
ARGS = dict(steps=250, seq=512, eval_count=16, save_every=25, threads=4, lr=2e-5)


def fail(reason):
    raise SystemExit(f"[BCI][BLOCK] {reason}")


def digest(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def import_at(name, path):
    if not path.is_file():
        fail(f"Missing dependency: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def checked_dependencies():
    if digest(ORIGINAL) != EXPECTED_LAUNCHER:
        fail("Existing Stage-3 launcher differs from verified v1.0; do not silently override it")
    if digest(CONTROLLER) != EXPECTED_CONTROLLER:
        fail("Existing training controller differs from verified v1.4; inspect before adapting")
    return import_at("bci_stage3_verified_v1", ORIGINAL), import_at("bci_stage3_controller_v1", CONTROLLER)


def summarize_source(raw, index, split):
    if raw.get("developer_seal") != SEAL or raw.get("split") != split:
        fail(f"Incorrect seal or split in {split} record #{index}")
    messages = raw.get("messages")
    if not isinstance(messages, list) or len(messages) < 4:
        fail(f"Missing episode messages in {split} record #{index}")
    if [m.get("role") for m in messages[:2]] != ["system", "user"]:
        fail(f"Incorrect episode opening roles: {split} #{index}")
    for message in messages:
        if message.get("role") not in ("system", "user", "assistant", "tool"):
            fail("Unexpected role in episode")
        if not isinstance(message.get("content"), str):
            fail("Non-string message content")
        if message["role"] == "tool":
            try:
                tool = json.loads(message["content"])
            except json.JSONDecodeError:
                fail("Malformed JSON tool result")
            if tool.get("simulated") is not True:
                fail("Tool result not explicitly marked simulated")
    assistants = [j for j, m in enumerate(messages) if m["role"] == "assistant"]
    if not assistants:
        fail("No assistant targets")
    # Cover tool decisions, post-tool analysis, and final reports across records.
    choice = (index - 1) % 4
    target_index = assistants[(0, min(1, len(assistants) - 1), len(assistants) // 2, len(assistants) - 1)[choice]]
    target = messages[target_index]["content"]
    try:
        json.loads(target)
        user = json.loads(messages[1]["content"])
    except json.JSONDecodeError:
        fail("Malformed JSON assistant target or user observation")
    obs = user.get("agent_observation", {})
    scope = obs.get("scope", {})
    parts = [
        "SYNTHETIC LAB FIXTURE: Nothing below was run on a real machine.",
        f"Task: {str(obs.get('task', 'unknown'))[:240]}",
        f"Category: {raw.get('category', 'unknown')}",
        f"Permissions: {json.dumps(scope.get('permissions', []), separators=(',', ':'))[:150]}",
        f"Network scope: {json.dumps(scope.get('network_scope', []), separators=(',', ':'))[:110]}",
    ]
    if target_index > 2:
        context = messages[max(2, target_index - 2):target_index]
        for prior in context:
            # Preserve role distinction, but bound source-context size for seq=512.
            parts.append(f"Prior {prior['role']} (synthetic): {prior['content'][:360]}")
    parts.append("Provide only the next assistant decision or report as JSON. Do not claim real execution.")
    system = (
        "You are BCI Nexus. Observe accurately; preserve faithfully; analyze transparently; "
        "communicate securely; act deliberately. Tool evidence here is simulated. "
        "Execute if and only if authorized scope, policy and side effects permit. "
        "Never claim commands were actually executed from fixtures."
    )
    return {
        "record_id": str(raw.get("record_id", "")),
        "source_group": str(raw.get("source_group", "")),
        "category": str(raw.get("category", "")),
        "projection_target": ["first_decision", "first_observation_update", "mid_episode", "final_report"][choice],
        "synthetic": True,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": "\n".join(parts)},
            {"role": "assistant", "content": target},
        ],
    }


def projection(source, controller):
    if DATA.exists():
        audit = DATA / "projection-audit.json"
        if not audit.is_file():
            fail("Existing projected dataset without audit; refusing overwrite")
        a = json.loads(audit.read_text())
        if a.get("source_zip_hash") != ZIP_HASH or a.get("projection_version") != VERSION:
            fail("Projection version/source mismatch; refusing overwrite")
        controller.verify(DATA)
        controller.scan_data([DATA])
        print("[BCI][PASS] Existing projected dataset verified", flush=True)
        return
    DATA.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stage3-projection-", dir=DATA.parent) as folder:
        temporary = Path(folder) / DATA.name
        temporary.mkdir()
        seen_ids = set()
        category_counts = Counter()
        role_counts = Counter()
        for split, expected in (("train", 9000), ("eval", 1000)):
            count = 0
            with (source / f"{split}.jsonl").open(encoding="utf-8") as inp, (temporary / f"{split}.jsonl").open("w", encoding="utf-8") as output:
                for line in inp:
                    if not line.strip():
                        continue
                    count += 1
                    record = json.loads(line)
                    new = summarize_source(record, count, split)
                    rid = new["record_id"]
                    if not rid or rid in seen_ids or not new["source_group"]:
                        fail("Missing/duplicate ID or source group")
                    seen_ids.add(rid)
                    role_counts[new["projection_target"]] += 1
                    category_counts[new["category"]] += 1
                    output.write(json.dumps(new, ensure_ascii=False, sort_keys=True) + "\n")
            if count != expected:
                fail(f"Wrong record count {split}: {count} != {expected}")
        write_json(temporary / "validation_report.json", {
            "blocking_structural_checks_pass": True,
            "status": "STRUCTURAL_PROJECTION_PASS_ONLY",
            "developer_seal": SEAL,
            "human_semantic_fact_review": "PENDING",
            "qwen3_tokenizer_validation": "PENDING",
            "original_dataset_production_ready": False,
            "synthetic_tool_evidence": True,
            "independent_holdout": False,
            "note": "Projection status only; no expert review has been performed",
        })
        with (temporary / "SHA256SUMS").open("w") as stream:
            for n in ("train.jsonl", "eval.jsonl", "validation_report.json"):
                stream.write(f"{digest(temporary / n)}  {n}\n")
        write_json(temporary / "projection-audit.json", {
            "source_zip_hash": ZIP_HASH,
            "projection_version": VERSION,
            "developer_seal": SEAL,
            "counts": category_counts,
            "projection_targets": role_counts,
            "synthetic": True,
            "semantic_review": "PENDING",
            "training_scope": "Synthetic demonstrations only; not evidence of actual tool execution",
        })
        controller.verify(temporary)
        controller.scan_data([temporary])
        temporary.rename(DATA)
    print("[BCI][PASS] Stage-3 projection: 9000 train / 1000 eval", flush=True)
    print(f"[BCI][DATA] {DATA}", flush=True)


def preflight_tokenizer(controller):
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE, local_files_only=True)
    results = {}
    for split, total in (("train", 9000), ("eval", 1000)):
        usable = 0
        for line in (DATA / f"{split}.jsonl").open(encoding="utf-8"):
            record = json.loads(line)
            if controller.encode(tokenizer, record, ARGS["seq"]) is not None:
                usable += 1
        results[split] = {"usable": usable, "total": total, "retention": usable / total}
        print(f"[BCI][TOKENIZER] {split}: usable={usable}/{total} ({usable/total:.1%})", flush=True)
    write_json(OUT / "stage3-tokenizer-preflight.json", results)
    if results["train"]["usable"] < 7200 or results["eval"]["usable"] < 800:
        fail("Token retention under 80% at seq=512. Review projection/sequence length first")
    print("[BCI][PASS] Tokenizer coverage meets controller requirement", flush=True)


def gate_isolation():
    ps = subprocess.run(["ps", "-eo", "pid=,args="], check=True, capture_output=True, text=True)
    for line in ps.stdout.splitlines():
        fields = line.strip().split(maxsplit=1)
        if len(fields) != 2:
            continue
        try:
            pid = int(fields[0])
        except ValueError:
            continue
        if pid == os.getpid():
            continue
        args = fields[1]
        if ("python" in args and ("/BCI/Nexus/chat.py" in args or
              "bci_nexus_post_interim_v1_4.py" in args or
              "BCI-Nexus-Stage3-Launcher-v1.0.py" in args or
              "BCI-Nexus-Stage3-Compatible-Handoff-v1.1.py" in args)):
            fail(f"Competing Nexus Python process PID={pid}")


def prepare(original, controller):
    original.source_gate()
    rawzip = original.archive_gate()
    original.extract(rawzip)
    folders = [p.parent for p in original.DATA.rglob("train.jsonl") if (p.parent / "SHA256SUMS").is_file()]
    if len(folders) != 1:
        fail(f"Expected one original dataset folder, got {len(folders)}")
    source = folders[0]
    controller.verify(source)
    report = json.loads((source / "validation_report.json").read_text())
    if report.get("status") != "STRUCTURAL_PASS" or report.get("production_ready") is not False:
        fail("Unexpected original validation report; do not override")
    projection(source, controller)
    preflight_tokenizer(controller)
    print("[BCI][READY] Projection prepared; expert semantic review still required", flush=True)


def train(original, controller):
    if os.environ.get("BCI_STAGE3_REVIEW_APPROVED") != "YES":
        fail("Review not approved; set BCI_STAGE3_REVIEW_APPROVED=YES only after review")
    gate_isolation()
    prepare(original, controller)
    controller.OUT = OUT
    args = argparse.Namespace(**ARGS)
    print("[BCI][START] Stage 3 from verified Stage-2 adapter (250 optimizer steps)", flush=True)
    adapter = controller.train_stage(DATA, original.SOURCE, 3, args)
    if adapter.resolve() != (STAGE / "step-000250" / "adapter").resolve():
        fail("Unexpected Stage-3 output adapter")
    before = json.loads((STAGE / "baseline-evaluation.json").read_text())
    after = json.loads((STAGE / "step-000250" / "evaluation.json").read_text())
    if not math.isfinite(before["loss"]) or not math.isfinite(after["loss"]) or after["loss"] > before["loss"] * 1.05:
        fail("Stage-3 evaluation failed to satisfy regression gate")
    write_json(OUT / "complete.json", {
        "status": "PASS", "seal": SEAL, "stage": 3,
        "source": str(original.SOURCE),
        "source_sha256": digest(original.SOURCE / "adapter_model.safetensors"),
        "final_adapter": str(adapter),
        "sha256": digest(adapter / "adapter_model.safetensors"),
        "baseline_loss": before["loss"], "final_loss": after["loss"],
        "synthetic_dataset": True, "semantic_review": "USER_ACKNOWLEDGED_NOT_INDEPENDENTLY_VERIFIED",
        "optimizer_steps": ARGS["steps"],
        "evaluation_note": "Synthetic template-overlap eval; not independent generalization evidence",
    })
    print("[BCI][PASS] Stage 3 completed; synthetic training only", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "train", "status"])
    options = parser.parse_args()
    if options.action == "status":
        complete = OUT / "complete.json"
        latest = STAGE / "latest.json"
        if complete.is_file():
            print(complete.read_text())
        elif latest.is_file():
            print("[BCI][PROGRESS]", json.loads(latest.read_text()).get("step"), "/250")
        else:
            print("[BCI][INFO] Stage 3 has no checkpoint yet")
        return
    original, controller = checked_dependencies()
    if options.action == "prepare":
        prepare(original, controller)
    else:
        train(original, controller)


if __name__ == "__main__":
    main()
