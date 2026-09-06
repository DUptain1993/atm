"""FTP anonymous login check."""

from __future__ import annotations

import ftplib

from agent.offensive.modules.base import ExploitModule
from agent.state import HostHit


class FtpAnonModule(ExploitModule):
    name = "ftp_anon"
    ports = (21,)

    def run(self, host: HostHit) -> bool:
        if 21 not in host.open_ports:
            return False
        try:
            ftp = ftplib.FTP(timeout=4.0)
            ftp.connect(host.ip, 21, timeout=4.0)
            ftp.login("anonymous", "anonymous@")
            ftp.quit()
            return True
        except Exception:
            return False
