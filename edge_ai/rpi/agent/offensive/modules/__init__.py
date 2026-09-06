"""Exploit modules for service-specific attack chains."""

from agent.offensive.modules.ftp_anon import FtpAnonModule
from agent.offensive.modules.http_defaults import HttpDefaultsModule
from agent.offensive.modules.http_sensitive import HttpSensitiveModule
from agent.offensive.modules.mongo_unauth import MongoUnauthModule
from agent.offensive.modules.mysql_defaults import MySqlDefaultsModule
from agent.offensive.modules.rdp_probe import RdpProbeModule
from agent.offensive.modules.redis_unauth import RedisUnauthModule
from agent.offensive.modules.smb_null import SmbNullModule
from agent.offensive.modules.snmp_public import SnmpPublicModule
from agent.offensive.modules.ssh_defaults import SshDefaultsModule
from agent.offensive.modules.telnet_defaults import TelnetDefaultsModule
from agent.offensive.modules.vnc_probe import VncProbeModule

MODULES = [
    SshDefaultsModule(),
    FtpAnonModule(),
    HttpDefaultsModule(),
    HttpSensitiveModule(),
    TelnetDefaultsModule(),
    RedisUnauthModule(),
    MongoUnauthModule(),
    MySqlDefaultsModule(),
    SmbNullModule(),
    SnmpPublicModule(),
    RdpProbeModule(),
    VncProbeModule(),
]

PORT_MAP: dict[int, list] = {}
for mod in MODULES:
    for port in mod.ports:
        PORT_MAP.setdefault(port, []).append(mod)
