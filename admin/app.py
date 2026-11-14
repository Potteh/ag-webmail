import os
import re
import secrets
import tempfile
from pathlib import Path
from typing import Annotated

import docker
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

app = FastAPI(title="AGMail Admin", docs_url=None, redoc_url=None, openapi_url=None)
security = HTTPBasic()
DOMAINS = Path("/data/domains.txt")
DOMAIN_RE = re.compile(r"^(?=.{4,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
ADDRESS_RE = re.compile(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@([a-zA-Z0-9.-]+)$")


def authorize(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    expected_user = os.environ.get("AGMAIL_ADMIN_USER", "")
    expected_password = os.environ.get("AGMAIL_ADMIN_PASSWORD", "")
    if not expected_user or len(expected_password) < 20 or not (
        secrets.compare_digest(credentials.username.encode(), expected_user.encode())
        and secrets.compare_digest(credentials.password.encode(), expected_password.encode())
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials",
                            headers={"WWW-Authenticate": "Basic"})
    return credentials.username


def domain_name(value: str) -> str:
    value = value.strip().lower()
    if not DOMAIN_RE.fullmatch(value):
        raise HTTPException(422, "Invalid domain")
    return value


def email_address(value: str) -> str:
    value = value.strip()
    match = ADDRESS_RE.fullmatch(value)
    if not match or len(value) > 254 or not DOMAIN_RE.fullmatch(match.group(1).lower()):
        raise HTTPException(422, "Invalid mailbox address")
    return value


def domains():
    if not DOMAINS.exists():
        return []
    return sorted(set(x.strip().lower() for x in DOMAINS.read_text().splitlines() if x.strip()))


def run_setup(*args: str) -> str:
    try:
        client = docker.from_env(timeout=30)
        container = client.containers.get("agmail-mailserver-1")
        result = container.exec_run(["setup", *args], stdout=True, stderr=True, demux=False)
        output = (result.output or b"").decode("utf-8", "replace")[:12000]
        if result.exit_code != 0:
            raise HTTPException(400, "Mail server command failed: " + output)
        return output
    except docker.errors.DockerException:
        raise HTTPException(503, "Mail server unavailable")


class DomainPayload(BaseModel):
    domain: str


class MailboxPayload(BaseModel):
    address: str
    password: str = Field(min_length=12, max_length=256)


@app.get("/", include_in_schema=False)
def home(_: str = Depends(authorize)):
    return FileResponse("/app/static/index.html", headers={"Cache-Control": "no-store"})


@app.get("/api/status")
def server_status(_: str = Depends(authorize)):
    try:
        client = docker.from_env(timeout=10)
        container = client.containers.get("agmail-mailserver-1")
        return {"status": container.status}
    except docker.errors.DockerException:
        return {"status": "unavailable"}


@app.get("/api/domains")
def list_domains(_: str = Depends(authorize)):
    return {"domains": domains()}


@app.post("/api/domains", status_code=201)
def add_domain(payload: DomainPayload, _: str = Depends(authorize)):
    domain = domain_name(payload.domain)
    current = domains()
    if domain in current:
        raise HTTPException(409, "Domain already registered")
    DOMAINS.parent.mkdir(parents=True, exist_ok=True)
    new = sorted(set(current + [domain]))
    fd, name = tempfile.mkstemp(dir=DOMAINS.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write("\n".join(new) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, DOMAINS)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return {"domain": domain, "note": "Configure MX, SPF, DKIM, DMARC and create a mailbox."}


@app.get("/api/mailboxes")
def list_mailboxes(_: str = Depends(authorize)):
    return {"output": run_setup("email", "list")}


@app.post("/api/mailboxes", status_code=201)
def add_mailbox(payload: MailboxPayload, _: str = Depends(authorize)):
    address = email_address(payload.address)
    if address.rsplit("@", 1)[1].lower() not in domains():
        raise HTTPException(400, "Register domain first")
    # Password is passed to docker exec and must never be logged or returned.
    run_setup("email", "add", address, payload.password)
    return {"address": address}


@app.put("/api/mailboxes/password")
def change_password(payload: MailboxPayload, _: str = Depends(authorize)):
    address = email_address(payload.address)
    run_setup("email", "update", address, payload.password)
    return {"address": address, "updated": True}
