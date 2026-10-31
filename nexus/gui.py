# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: Unified Nexus / Sentinel / BCIBot / BCILock GUI v0.5.2
"""One native Sentinel QMainWindow with three additional Nexus workspaces."""
from __future__ import annotations
import importlib.util
import ast
import inspect
import json
import os
from pathlib import Path
import sys
from . import agent_client, core, training, swarm

def _supports_nexus_extension(folder: Path) -> bool:
    """Inspect Sentinel's hook signature without importing or launching a window."""
    source = folder / "sentinel_gui.py"
    if not source.is_file() or not (folder / "network_scope.py").is_file():
        return False
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    except (SyntaxError, UnicodeError, OSError):
        return False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main":
            parameters = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            return any(parameter.arg == "nexus_extension" for parameter in parameters)
    return False


def _reset_prompt_after_dispatch(prompt_widget) -> None:
    """Clear and focus a prompt if and only if dispatch was accepted."""
    prompt_widget.clear()
    prompt_widget.setFocus()


def sentinel_path() -> Path:
    """Select Sentinel if and only if its single-window Nexus hook exists."""
    override = os.environ.get("BCI_SENTINEL_DIR")
    if override:
        directory = Path(override).expanduser()
        if _supports_nexus_extension(directory):
            return directory
        raise RuntimeError(
            "BCI_SENTINEL_DIR points to an incompatible checkout: " +
            str(directory) + ". Update it or select $HOME/BCI/BCISentinel-."
        )

    base = Path.home() / "BCI"
    directories = [
        base / "BCISentinel-",
        base / "BCISentinel",
        base / "orbital",
        base / "Docker Projects/orbital",
    ]
    for directory in directories:
        if _supports_nexus_extension(directory):
            return directory
    found = [str(p) for p in directories if (p / "sentinel_gui.py").is_file()]
    if found:
        raise RuntimeError(
            "All Sentinel checkouts are missing main(nexus_extension=...): " +
            ", ".join(found) + ". Update BCISentinel- or set BCI_SENTINEL_DIR."
        )
    raise FileNotFoundError(
        "No Sentinel checkout found. Clone BCISentinel- under $HOME/BCI."
    )


def launch() -> None:
    from PyQt6.QtCore import QThread, pyqtSignal
    from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QPushButton, QPlainTextEdit, QTextEdit, QLineEdit, QMessageBox)

    class Worker(QThread):
        done = pyqtSignal(object)
        failed = pyqtSignal(str)
        def __init__(self, fn, parent):
            super().__init__(parent)
            self.fn = fn
        def run(self):
            try:
                self.done.emit(self.fn())
            except Exception as exc:
                self.failed.emit(type(exc).__name__ + ": " + str(exc)[:300])

    class Panel(QWidget):
        def __init__(self, title, subtitle, parent=None):
            super().__init__(parent)
            self._workers = []
            self.setObjectName("nexusWorkspace")
            self.setStyleSheet(
                "QWidget#nexusWorkspace {background: #12101c; border: 1px solid #51213e; "
                "border-radius: 13px;} "
                "QLabel {color: #ebefff;} QPushButton {background: #241728; "
                "border: 1px solid #00d6ed; border-radius: 8px; padding: 9px; color: #00e5f9;} "
                "QPlainTextEdit, QTextEdit, QLineEdit {background: #090d18; "
                "border: 1px solid #693451; border-radius: 8px; color: #deefff;}")
            self.layout_main = QVBoxLayout(self)
            self.layout_main.setContentsMargins(18, 18, 18, 18)
            heading = QLabel(title)
            heading.setStyleSheet("font-size: 21px; color: #00edff; font-weight: 700;")
            self.layout_main.addWidget(heading)
            description = QLabel(subtitle)
            description.setWordWrap(True)
            self.layout_main.addWidget(description)

        def submit(self, fn, success, failure=None):
            worker = Worker(fn, self)
            self._workers.append(worker)
            worker.done.connect(success)
            worker.failed.connect(failure or self.warning)
            worker.finished.connect(lambda w=worker: self._workers.remove(w)
                                    if w in self._workers else None)
            worker.finished.connect(worker.deleteLater)
            worker.start()

        def warning(self, message):
            QMessageBox.warning(self, "BCI Nexus", message)

    class Overview(Panel):
        def __init__(self, parent):
            super().__init__("◆ BCI NEXUS • OPERATIONS",
                "One console. Sentinel telemetry, Docker AI and native BCILock security.", parent)
            self.output = QPlainTextEdit()
            self.output.setReadOnly(True)
            self.layout_main.addWidget(self.output)
            refresh = QPushButton("Refresh all component observations")
            refresh.clicked.connect(self.refresh)
            self.layout_main.addWidget(refresh)
            self.refresh()

        def refresh(self):
            self.submit(core.overall_status,
                lambda data: self.output.setPlainText(json.dumps(data, indent=2)),
                lambda error: self.output.setPlainText("Status unavailable: " + error))

    class Bot(Panel):
        def __init__(self, parent):
            super().__init__("◈ BCIBOT • CONTAINER AGENT",
                "Ask the unified model or execute an approved Bash command INSIDE Docker. "
                "This is not a Kali host shell.", parent)
            self.health = QLabel("Docker agent: unchecked")
            self.layout_main.addWidget(self.health)
            check = QPushButton("Check Docker agent")
            check.clicked.connect(self.check)
            self.layout_main.addWidget(check)
            self.chat = QPlainTextEdit()
            self.chat.setReadOnly(True)
            self.layout_main.addWidget(self.chat, 1)
            self.question = QTextEdit()
            self.question.setMaximumHeight(75)
            self.question.setPlaceholderText("Ask BCIBot a question…")
            self.layout_main.addWidget(self.question)
            send = QPushButton("Ask BCIBot")
            send.clicked.connect(self.ask)
            self.layout_main.addWidget(send)
            self.terminal = QPlainTextEdit()
            self.terminal.setReadOnly(True)
            self.layout_main.addWidget(self.terminal, 1)
            command_row = QHBoxLayout()
            self.command = QLineEdit()
            self.command.setPlaceholderText("Bash in /workspace (Docker only)")
            self.command.returnPressed.connect(self.shell)
            command_row.addWidget(self.command)
            execute = QPushButton("Execute in container")
            execute.clicked.connect(self.shell)
            command_row.addWidget(execute)
            self.layout_main.addLayout(command_row)
            self.check()

        def check(self):
            self.submit(agent_client.health,
                lambda obj: self.health.setText(
                    "Docker agent: CONNECTED | scope=" + str(obj.get("scope"))),
                lambda error: self.health.setText("Docker agent: OFFLINE — " + error))

        def ask(self):
            q = self.question.toPlainText().strip()
            if not q:
                return
            self.chat.appendPlainText("YOU: " + q)
            try:
                job = swarm.plan(q)
            except (ValueError, RuntimeError, OSError) as exc:
                self.chat.appendPlainText("SWARM PLAN ERROR: " + str(exc) + "\n")
                return
            approved = False
            if job.host:
                target = job.host
                details = ("NATIVE KALI OBSERVATION\n" +
                    "Scope: " + target.target + "\nInterface: " + target.interface +
                    "\nCommand: " + " ".join(target.argv) +
                    "\n\nApprove only if you own or are authorized to assess this network.")
                decision = QMessageBox.question(
                    self, "BCI swarm: approve host observer", details,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                if decision != QMessageBox.StandardButton.Yes:
                    self.chat.appendPlainText("SWARM: Declined; no tool executed.\n")
                    return
                approved = True
            self.chat.appendPlainText("SWARM " + job.id[:10] +
                                      ": " + " / ".join(job.roles) + "\n")
            self.submit(lambda j=job, a=approved: swarm.execute(j, approved=a),
                lambda obj: self.chat.appendPlainText(
                    "SWARM [" + str(obj.get("source")) +
                    " | findings_verified=" + str(obj.get("verified", False)) +
                    " | tool_execution_succeeded=" +
                    str(obj.get("execution_succeeded", False)) +
                    " | response_shape_valid=" +
                    str(obj.get("response_shape_valid", False)) + "]\n" +
                    (str(obj["observation"].get("stdout", "")) +
                     str(obj["observation"].get("stderr", ""))
                     if "observation" in obj else
                     "\n".join(r["role"].upper() + " [ADVISORY]: " +
                               r["text"] for r in obj["reports"])) + "\n"),
                lambda error: self.chat.appendPlainText(
                    "SWARM ERROR: " + error + "\n"))
            # An accepted request has been submitted to the worker.
            # Keep text intact when planning failed or the operator declined.
            _reset_prompt_after_dispatch(self.question)

        def shell(self):
            command = self.command.text().strip()
            if not command:
                return
            answer = QMessageBox.question(self, "Container command confirmation",
                "Run inside BCIBot Docker container?\n\n" + command[:600],
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if answer != QMessageBox.StandardButton.Yes:
                return
            self.terminal.appendPlainText("$ " + command)
            self.submit(lambda: agent_client.shell(command),
                lambda obj: self.terminal.appendPlainText(
                    str(obj.get("stdout", "")) + str(obj.get("stderr", "")) +
                    "\n[Docker exit=" + str(obj.get("exit_code")) + "]\n"))

    class Lock(Panel):
        def __init__(self, parent):
            super().__init__("◇ BCILOCK • HOST SECURITY",
                "Read-only evidence; Bluetooth authentication and nftables remain on Kali.", parent)
            self.output = QPlainTextEdit()
            self.output.setReadOnly(True)
            self.layout_main.addWidget(self.output)
            refresh = QPushButton("Refresh BCILock evidence")
            refresh.clicked.connect(self.refresh)
            self.layout_main.addWidget(refresh)
            self.refresh()

        def refresh(self):
            def inspect_lock():
                payload = core._limited_status_command()
                return {"fresh": core.telemetry_fresh(payload),
                        "summary": core.lock_summary(payload)}
            self.submit(inspect_lock,
                lambda obj: self.output.setPlainText(json.dumps(obj, indent=2)),
                lambda error: self.output.setPlainText("Unavailable: " + error))

    class Training(Panel):
        def __init__(self, parent):
            super().__init__("◇ BCIBOT • MODEL TRAINING",
                "Persistent datasets, LoRA adapters, checkpoints, and run logs. "
                "Production model replacement requires evaluation and explicit approval.", parent)
            self.output = QPlainTextEdit()
            self.output.setReadOnly(True)
            self.layout_main.addWidget(self.output)
            refresh = QPushButton("Inspect saved training artifacts")
            refresh.clicked.connect(self.refresh)
            self.layout_main.addWidget(refresh)
            self.refresh()

        def refresh(self):
            self.submit(training.status,
                lambda obj: self.output.setPlainText(json.dumps(obj, indent=2)),
                lambda error: self.output.setPlainText("Unavailable: " + error))

    def extend(window):
        window.setWindowTitle("BEACON COMPUTING INITIATIVE — BCI NEXUS")
        window.resize(1580, 940)
        window.tabs.insertTab(0, Overview(window), "◆ Nexus")
        window.tabs.addTab(Bot(window), "◈ BCIBot + Shell")
        window.tabs.addTab(Lock(window), "◇ BCILock")
        window.tabs.addTab(Training(window), "◉ Model Training")
        window.tabs.setCurrentIndex(0)

    folder = sentinel_path()
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
    spec = importlib.util.spec_from_file_location("bci_embedded_sentinel", folder / "sentinel_gui.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import Sentinel GUI")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # A fresh Sentinel source clone may be separate from the live capture mount.
    # Redirect the observation file if and only if a real local state file exists.
    explicit = os.environ.get("BCI_SENTINEL_STATE")
    existing = Path(module.STATE_FILE_PATH)
    legacy = Path.home() / "BCI/Docker Projects/orbital/captures/bci_state.json"
    if explicit:
        candidate = Path(explicit).expanduser()
        if not candidate.is_file():
            raise FileNotFoundError("BCI_SENTINEL_STATE does not exist: " + str(candidate))
        module.STATE_FILE_PATH = str(candidate)
    elif not existing.is_file() and legacy.is_file():
        module.STATE_FILE_PATH = str(legacy)
    if "nexus_extension" not in inspect.signature(module.main).parameters:
        raise RuntimeError("Sentinel GUI is outdated; pull its latest main branch")
    module.main(nexus_extension=extend)

def main() -> int:
    try:
        launch()
        return 0
    except (FileNotFoundError, ImportError, RuntimeError) as exc:
        print("[BCI] GUI error: " + str(exc), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
