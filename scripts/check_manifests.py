"""Validate the Kubernetes manifests the curriculum teaches.

Week 9's challenge asks students to adapt "Session 1's manifests" for their own
app. Those manifests lived only as a string inside a notebook, which meant
nothing checked that they parsed -- let alone that they would survive the
platform review the module is preparing people for.

This runs in CI. It parses the YAML and asserts the properties a bank's platform
team greps for. When one of these fails, the fix is the manifest, not the check.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from textwrap import dedent

# Windows consoles default to a code page that cannot encode the check marks
# these scripts print, so a redirected run dies with UnicodeEncodeError before
# reporting anything. Force UTF-8 on our own output rather than dropping to
# ASCII markers -- the students on managed Windows laptops are the ones running
# these gates.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OK, BAD = "✓", "✗"

SOURCES = [ROOT / "09_Infrastructure/sessions/S1_From_Container_to_Cluster.py"]


def extract(path: Path) -> list[tuple[str, str]]:
    """Every `NAME = dedent(\"\"\"...\"\"\")` block that looks like Kubernetes YAML."""
    out = []
    for match in re.finditer(r'(\w+) = dedent\("""(.*?)"""\)', path.read_text("utf-8"), re.S):
        body = dedent(match.group(2)).strip()
        if "apiVersion:" in body and "kind:" in body:
            out.append((match.group(1), body))
    return out


def check(name: str, docs: list[dict]) -> list[str]:
    problems: list[str] = []
    kinds = {doc.get("kind") for doc in docs if doc}
    deployments = [doc for doc in docs if doc and doc.get("kind") == "Deployment"]

    if not deployments:
        return [f"{name}: no Deployment found"]

    for dep in deployments:
        pod = dep["spec"]["template"]["spec"]
        pod_sc = pod.get("securityContext") or {}
        containers = pod.get("containers") or []
        if not pod_sc.get("runAsNonRoot"):
            problems.append(
                f"{name}: pod has no `runAsNonRoot: true`. Containers run as root "
                f"by default and this is the most common enterprise review finding."
            )
        for container in containers:
            sc = container.get("securityContext") or {}
            if not sc.get("readOnlyRootFilesystem"):
                problems.append(f"{name}: container `{container.get('name')}` has no readOnlyRootFilesystem")
            if (sc.get("capabilities") or {}).get("drop") != ["ALL"]:
                problems.append(f"{name}: container `{container.get('name')}` does not drop ALL capabilities")
            if sc.get("allowPrivilegeEscalation") is not False:
                problems.append(f"{name}: container `{container.get('name')}` allows privilege escalation")
            if ":latest" in str(container.get("image", "")) or ":" not in str(container.get("image", "")):
                problems.append(f"{name}: container `{container.get('name')}` image is not pinned to a tag")
            res = container.get("resources") or {}
            if "limits" not in res or "requests" not in res:
                problems.append(f"{name}: container `{container.get('name')}` missing resource requests/limits")
            if "readinessProbe" not in container or "livenessProbe" not in container:
                problems.append(f"{name}: container `{container.get('name')}` missing a probe")

        if (dep["spec"].get("replicas") or 1) > 1 and "PodDisruptionBudget" not in kinds:
            problems.append(
                f"{name}: replicas > 1 but no PodDisruptionBudget. A node drain can "
                f"evict every replica at once, so the extra replica buys nothing "
                f"during the upgrade it was supposed to survive."
            )
    return problems


def main() -> int:
    try:
        import yaml
    except ModuleNotFoundError:
        print(f"{BAD} PyYAML is required:  uv sync --group dev")
        return 1

    total, failures = 0, []
    for path in SOURCES:
        if not path.exists():
            continue
        for name, body in extract(path):
            total += 1
            try:
                docs = list(yaml.safe_load_all(body))
            except yaml.YAMLError as exc:
                failures.append(f"{name} in {path.name} is not valid YAML: {exc}")
                continue
            failures.extend(check(f"{path.name}:{name}", docs))

    for problem in failures:
        print(f"{BAD} {problem}")
    if failures:
        return 1
    print(f"{OK} {total} manifest block(s) parse and pass the platform-review checklist")
    return 0


if __name__ == "__main__":
    sys.exit(main())
