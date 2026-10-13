"""What your network allows, established without hanging your notebook.

Tier 2 by convention. Standard library only — it has to run before anything is
installed, on a machine that may not be able to install anything.

Week 1 Session 1 writes this probe from scratch, and Week 9's challenge re-runs
it against the environment the app will actually deploy into. That second use is
why it lives here: TC9's ecosystem checklist is the same questions asked of a
different network, and nobody should rewrite the probe to ask them.

**The hard deadline is the feature.** A serial probe on a locked-down corporate
network — which is the case this exists for — can hang for minutes, because
`socket.gethostbyname` does not honour `socket.setdefaulttimeout` and a
blackholed DNS query blocks until the system resolver gives up. A diagnostic
tool that hangs on exactly the machines it was written to diagnose is worse than
no tool, because the student concludes their environment is broken in some new
way and stops. Every probe here runs in a worker with a wall-clock deadline and
reports `timeout` rather than blocking.

**Naming the interceptor is the point.** "TLS succeeded" is not the interesting
result on a managed laptop. *Who signed it* is. A corporate proxy re-signs every
certificate with an internal CA, which is why `pip` works in the terminal and
fails inside a container that does not trust that CA — a Week 1 mystery that
becomes a Week 9 conversation.
"""

from __future__ import annotations

import os
import queue
import socket
import ssl
import threading
import time
from dataclasses import dataclass, field

# Hosts every week of this course eventually needs.
DEFAULT_HOSTS: tuple[tuple[str, str], ...] = (
    ("pypi.org", "Python packages"),
    ("files.pythonhosted.org", "the actual wheel downloads"),
    ("api.openai.com", "the model API"),
    ("cdn.jsdelivr.net", "the CDN your app's frontend uses"),
    ("huggingface.co", "open weights and fine-tuning"),
    ("registry-1.docker.io", "container images"),
    ("github.com", "this repository"),
)

# Issuer organisations that are public certificate authorities. Anything else
# signing a public site means something is terminating your TLS.
PUBLIC_CAS = (
    "digicert", "let's encrypt", "isrg", "google trust services", "amazon",
    "sectigo", "comodo", "globalsign", "cloudflare", "microsoft", "baltimore",
    "usertrust", "godaddy", "entrust", "identrust", "starfield", "verisign",
    "thawte", "geotrust", "rapidssl", "buypass", "actalis", "certum",
)

# Environment variables that reveal a proxy or a swapped trust store.
PROXY_VARS = (
    "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "no_proxy",
    "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE",
    "NODE_EXTRA_CA_CERTS", "PIP_INDEX_URL", "PIP_TRUSTED_HOST",
    "UV_INDEX_URL", "UV_DEFAULT_INDEX",
)


@dataclass
class Probe:
    host: str
    why: str = ""
    ip: str | None = None
    dns_ok: bool = False
    tls_ok: bool = False
    issuer: str = ""
    error: str = ""

    @property
    def intercepted(self) -> bool:
        """True when a public site was signed by something that is not a public CA."""
        if not self.tls_ok or not self.issuer:
            return False
        low = self.issuer.lower()
        return not any(ca in low for ca in PUBLIC_CAS)

    @property
    def status(self) -> str:
        if not self.dns_ok:
            return "DNS BLOCKED"
        if not self.tls_ok:
            return "TLS BLOCKED"
        return "INTERCEPTED" if self.intercepted else "OK"


@dataclass
class Report:
    probes: list = field(default_factory=list)
    proxy_env: dict = field(default_factory=dict)

    @property
    def blocked(self) -> list:
        return [probe for probe in self.probes if not probe.tls_ok]

    @property
    def intercepted(self) -> list:
        return [probe for probe in self.probes if probe.intercepted]

    def __str__(self) -> str:
        bits = [f"{len(self.probes) - len(self.blocked)}/{len(self.probes)} reachable"]
        if self.intercepted:
            names = sorted({probe.issuer for probe in self.intercepted})
            bits.append(f"TLS intercepted by {', '.join(names)}")
        if self.proxy_env:
            bits.append(f"{len(self.proxy_env)} proxy/CA variables set")
        return " · ".join(bits)

    def verdict(self) -> str:
        """The sentence to paste into use_case/ecosystem.md."""
        if self.blocked:
            hosts = ", ".join(probe.host for probe in self.blocked)
            return (
                f"Blocked: {hosts}. Someone has to allow these or mirror them "
                f"internally before Weeks 2, 8, and 9 — find out who, now, not "
                f"in the week you need it."
            )
        if self.intercepted:
            names = ", ".join(sorted({probe.issuer for probe in self.intercepted}))
            return (
                f"TLS is terminated by {names}. Everything works in your terminal "
                f"because your OS trusts that CA. It will fail inside a container, "
                f"which does not — you will need that CA baked in or mounted. This "
                f"is a Week 9 conversation you can start now."
            )
        return "Open network, public CAs, no proxy. Nothing here will bite you."


def _one(host: str, why: str, timeout: float) -> Probe:
    probe = Probe(host=host, why=why)
    try:
        # getaddrinfo rather than gethostbyname: it is the modern call, it
        # returns IPv6 too, and the failure is a clean exception.
        info = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        probe.ip = info[0][4][0]
        probe.dns_ok = True
    except Exception as exc:
        probe.error = f"{type(exc).__name__}"
        return probe

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=timeout) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as tls:
                probe.tls_ok = True
                cert = tls.getpeercert() or {}
                for field_ in cert.get("issuer", ()):
                    for key, value in field_:
                        if key == "organizationName":
                            probe.issuer = value
    except Exception as exc:
        probe.error = f"{type(exc).__name__}: {exc}"[:80]
    return probe


def check_egress(hosts=DEFAULT_HOSTS, *, timeout: float = 6.0,
                 workers: int = 8) -> Report:
    """Probe every host concurrently, with a wall-clock deadline for the batch.

    The deadline is enforced here rather than by the socket, because DNS
    resolution ignores socket timeouts entirely -- a blackholed lookup blocks
    until the system resolver gives up, which on a managed network can be tens
    of seconds. A probe that misses the deadline is abandoned mid-call and
    reported as blocked.

    **Abandoning it has to be real, and that is why this uses raw threads
    rather than a `ThreadPoolExecutor`.** A pool's workers are not daemon
    threads, and since Python 3.9 `concurrent.futures.thread` registers an
    atexit hook that joins every one of them. `shutdown(wait=False)` returns
    immediately, then the interpreter blocks on the way out -- which moves the
    hang this module exists to prevent from the middle of the run to the end of
    it, where it is harder to explain. These threads are `daemon=True` and
    nothing joins them, so a stuck `getaddrinfo` cannot delay exit.
    """
    hosts = tuple(hosts)
    report = Report()
    if not hosts:
        report.proxy_env = _proxy_env()
        return report

    todo: queue.Queue = queue.Queue()
    for index, (host, why) in enumerate(hosts):
        todo.put((index, host, why))
    done: queue.Queue = queue.Queue()

    def worker() -> None:
        while True:
            try:
                index, host, why = todo.get_nowait()
            except queue.Empty:
                return
            try:
                done.put((index, _one(host, why, timeout)))
            except BaseException as exc:      # a worker must never die silently
                done.put((index, Probe(host=host, why=why,
                                       error=f"{type(exc).__name__}: {exc}"[:80])))

    for thread_number in range(max(1, min(workers, len(hosts)))):
        threading.Thread(target=worker, name=f"preflight-{thread_number}",
                         daemon=True).start()

    budget = timeout * 2 + 2                  # generous, but bounded
    deadline = time.monotonic() + budget
    collected: dict[int, Probe] = {}
    while len(collected) < len(hosts):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            index, probe = done.get(timeout=remaining)
        except queue.Empty:
            break
        collected[index] = probe

    # Whatever did not answer is still a finding: name it, do not drop it.
    for index, (host, why) in enumerate(hosts):
        if index not in collected:
            collected[index] = Probe(
                host=host, why=why,
                error=f"no answer within {budget:.0f}s — treat as blocked",
            )
    report.probes = [collected[index] for index in range(len(hosts))]
    report.proxy_env = _proxy_env()
    return report


def _proxy_env() -> dict[str, str]:
    """The proxy and trust-store variables actually set, counted once each.

    PROXY_VARS lists HTTPS_PROXY and https_proxy because on Unix they are two
    different variables. Windows environment lookup is case-insensitive, so one
    variable answers to both names and gets counted twice -- telling a student
    they have eight proxy settings when they have four. Collapse a repeat only
    when the value matches; genuinely divergent casings on Unix are worth
    seeing.
    """
    seen: dict[str, str] = {}
    env: dict[str, str] = {}
    for name in PROXY_VARS:
        value = os.environ.get(name)
        if not value or seen.get(name.upper()) == value:
            continue
        seen[name.upper()] = value
        env[name] = value
    return env
