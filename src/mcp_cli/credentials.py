"""Manage MCP server credentials in ~/.mcps/credentials (INI format, chmod 600)."""

import configparser
import os
from dataclasses import dataclass

CREDS_DIR = os.path.expanduser("~/.mcps")
CREDS_FILE = os.path.join(CREDS_DIR, "credentials")


@dataclass
class ServerCredentials:
    url: str
    token: str


def save(server_name: str, url: str, token: str) -> None:
    os.makedirs(CREDS_DIR, mode=0o700, exist_ok=True)
    cfg = configparser.ConfigParser()
    if os.path.isfile(CREDS_FILE):
        cfg.read(CREDS_FILE)
    if server_name not in cfg:
        cfg[server_name] = {}
    cfg[server_name]["url"] = url
    cfg[server_name]["token"] = token
    with open(CREDS_FILE, "w") as f:
        cfg.write(f)
    os.chmod(CREDS_FILE, 0o600)


def load(server_name: str) -> ServerCredentials:
    cfg = configparser.ConfigParser()
    if not os.path.isfile(CREDS_FILE):
        raise FileNotFoundError(f"Missing {CREDS_FILE}")
    cfg.read(CREDS_FILE)
    if server_name not in cfg:
        raise KeyError(f"No section [{server_name}] in {CREDS_FILE}")
    return ServerCredentials(
        url=cfg[server_name]["url"],
        token=cfg[server_name]["token"],
    )
