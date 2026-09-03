"""
catalogo.py — base de conhecimento sobre portas.

Por que este arquivo existe separado: o /etc/services do sistema diz apenas
"qual nome IANA tem este número". Ele NÃO diz se expor aquela porta na internet
é uma boa ideia. Essa segunda informação é julgamento profissional, não dado
de registro — e é ela que transforma uma lista de portas em um relatório útil.

Regra de leitura: `risco` é o risco de a porta estar acessível a partir de uma
rede não confiável (0.0.0.0 ou IP público). Uma porta de risco ALTO escutando
apenas em 127.0.0.1 é normal e esperada.
"""

from dataclasses import dataclass

ALTO = "ALTO"
MEDIO = "MEDIO"
BAIXO = "BAIXO"


@dataclass(frozen=True)
class Servico:
    nome: str
    proto_app: str        # protocolo de aplicação que roda em cima do transporte
    descricao: str
    risco_exposto: str    # risco de estar aberto para rede não confiável
    porta_segura: int | None = None   # variante com TLS, quando existe


# Chave: (numero, "tcp"|"udp")
CATALOGO: dict[tuple[int, str], Servico] = {
    (20, "tcp"): Servico("ftp-data", "FTP", "Canal de dados do FTP (modo ativo).", ALTO, 989),
    (21, "tcp"): Servico("ftp", "FTP", "Transferência de arquivos. Credenciais em texto claro.", ALTO, 990),
    (22, "tcp"): Servico("ssh", "SSH", "Shell remoto e SFTP/SCP. Criptografado.", MEDIO),
    (23, "tcp"): Servico("telnet", "Telnet", "Shell remoto SEM criptografia. Obsoleto desde os anos 1990.", ALTO, 992),
    (25, "tcp"): Servico("smtp", "SMTP", "Entrega de e-mail entre servidores (MTA a MTA).", MEDIO, 465),
    (53, "tcp"): Servico("domain", "DNS", "DNS sobre TCP: respostas grandes e transferência de zona.", ALTO, 853),
    (53, "udp"): Servico("domain", "DNS", "DNS sobre UDP: o caminho normal das consultas.", ALTO, 853),
    (67, "udp"): Servico("bootps", "DHCP", "Servidor DHCP (recebe pedidos do cliente).", MEDIO),
    (68, "udp"): Servico("bootpc", "DHCP", "Cliente DHCP (recebe a oferta do servidor).", BAIXO),
    (69, "udp"): Servico("tftp", "TFTP", "FTP trivial, sem autenticação. Usado em boot de rede.", ALTO),
    (80, "tcp"): Servico("http", "HTTP", "Web sem criptografia.", MEDIO, 443),
    (110, "tcp"): Servico("pop3", "POP3", "Leitura de e-mail, baixa e apaga.", ALTO, 995),
    (111, "tcp"): Servico("sunrpc", "ONC RPC", "Portmapper. Revela outros serviços RPC.", ALTO),
    (123, "udp"): Servico("ntp", "NTP", "Sincronismo de relógio. Vetor clássico de amplificação DDoS.", MEDIO),
    (135, "tcp"): Servico("epmap", "MS RPC", "Mapeador de endpoints RPC da Microsoft.", ALTO),
    (137, "udp"): Servico("netbios-ns", "NetBIOS", "Resolução de nomes NetBIOS. Legado.", ALTO),
    (138, "udp"): Servico("netbios-dgm", "NetBIOS", "Datagramas NetBIOS. Legado.", ALTO),
    (139, "tcp"): Servico("netbios-ssn", "NetBIOS/SMB", "SMB sobre NetBIOS. Legado; use 445.", ALTO),
    (143, "tcp"): Servico("imap", "IMAP", "Leitura de e-mail, mantém no servidor.", ALTO, 993),
    (161, "udp"): Servico("snmp", "SNMP", "Monitoração. v1/v2c usam 'community string' em texto claro.", ALTO),
    (162, "udp"): Servico("snmptrap", "SNMP", "Recepção de traps SNMP.", MEDIO),
    (389, "tcp"): Servico("ldap", "LDAP", "Diretório. Sem TLS, credenciais viajam legíveis.", ALTO, 636),
    (443, "tcp"): Servico("https", "HTTP/TLS", "Web com TLS. HTTP/1.1 e HTTP/2.", BAIXO),
    (443, "udp"): Servico("https", "HTTP/3 (QUIC)", "Web sobre QUIC. Mesmo número, transporte diferente.", BAIXO),
    (445, "tcp"): Servico("microsoft-ds", "SMB", "Compartilhamento de arquivos Windows. Alvo de EternalBlue/WannaCry.", ALTO),
    (465, "tcp"): Servico("submissions", "SMTP/TLS", "Envio de e-mail pelo cliente, TLS implícito.", MEDIO),
    (514, "udp"): Servico("syslog", "Syslog", "Log remoto sem autenticação nem criptografia.", MEDIO),
    (587, "tcp"): Servico("submission", "SMTP/STARTTLS", "Envio de e-mail pelo cliente (RFC 6409).", MEDIO),
    (631, "tcp"): Servico("ipp", "IPP", "Impressão (CUPS). Costuma estar aberto sem ninguém saber.", MEDIO),
    (636, "tcp"): Servico("ldaps", "LDAP/TLS", "LDAP com TLS implícito.", MEDIO),
    (853, "tcp"): Servico("domain-s", "DoT", "DNS over TLS (RFC 7858).", BAIXO),
    (993, "tcp"): Servico("imaps", "IMAP/TLS", "IMAP com TLS implícito.", MEDIO),
    (995, "tcp"): Servico("pop3s", "POP3/TLS", "POP3 com TLS implícito.", MEDIO),
    (1433, "tcp"): Servico("ms-sql-s", "TDS", "Microsoft SQL Server.", ALTO),
    (1521, "tcp"): Servico("oracle", "TNS", "Oracle Database Listener.", ALTO),
    (1883, "tcp"): Servico("mqtt", "MQTT", "Mensageria IoT. Sem TLS por padrão.", ALTO, 8883),
    (2049, "tcp"): Servico("nfs", "NFS", "Sistema de arquivos de rede.", ALTO),
    (2375, "tcp"): Servico("docker", "Docker API", "API do Docker SEM TLS. Equivale a root remoto na máquina.", ALTO, 2376),
    (2376, "tcp"): Servico("docker-s", "Docker API", "API do Docker com TLS mútuo.", ALTO),
    (3000, "tcp"): Servico("(dev)", "HTTP", "Convenção de dev: Node, Rails, Grafana.", MEDIO),
    (3306, "tcp"): Servico("mysql", "MySQL", "MySQL/MariaDB.", ALTO),
    (3389, "tcp"): Servico("ms-wbt-server", "RDP", "Área de trabalho remota Windows. Alvo nº 1 de ransomware.", ALTO),
    (4369, "tcp"): Servico("epmd", "EPMD", "Erlang Port Mapper (RabbitMQ). Revela portas internas.", ALTO),
    (5000, "tcp"): Servico("(dev)", "HTTP", "Flask, .NET dev, registry Docker. No macOS: AirPlay Receiver.", MEDIO),
    (5432, "tcp"): Servico("postgresql", "PostgreSQL", "PostgreSQL.", ALTO),
    (5601, "tcp"): Servico("kibana", "HTTP", "Kibana. Sem auth em versões antigas.", ALTO),
    (5672, "tcp"): Servico("amqp", "AMQP", "RabbitMQ.", ALTO, 5671),
    (5900, "tcp"): Servico("vnc", "RFB", "VNC. Senha de 8 caracteres, sem criptografia.", ALTO),
    (6379, "tcp"): Servico("redis", "RESP", "Redis. Sem senha por padrão até a versão 6.", ALTO),
    (6443, "tcp"): Servico("kube-apiserver", "HTTPS", "API do Kubernetes.", ALTO),
    (8000, "tcp"): Servico("(dev)", "HTTP", "python -m http.server, Django.", MEDIO),
    (8080, "tcp"): Servico("http-alt", "HTTP", "HTTP alternativo, Tomcat, proxies.", MEDIO),
    (8443, "tcp"): Servico("https-alt", "HTTPS", "HTTPS alternativo.", BAIXO),
    (8883, "tcp"): Servico("secure-mqtt", "MQTT/TLS", "MQTT com TLS.", MEDIO),
    (9000, "tcp"): Servico("(vários)", "HTTP/FastCGI", "MinIO, SonarQube, PHP-FPM, Portainer.", MEDIO),
    (9090, "tcp"): Servico("prometheus", "HTTP", "Prometheus. Sem autenticação por padrão.", ALTO),
    (9092, "tcp"): Servico("kafka", "Kafka", "Apache Kafka.", ALTO),
    (9200, "tcp"): Servico("elasticsearch", "HTTP", "Elasticsearch. Sem auth em versões < 8.", ALTO),
    (11211, "tcp"): Servico("memcached", "memcached", "Memcached. Amplificação DDoS recorde em 2018.", ALTO),
    (11211, "udp"): Servico("memcached", "memcached", "UDP desabilitado por padrão desde 2018 — por bom motivo.", ALTO),
    (27017, "tcp"): Servico("mongodb", "MongoDB Wire", "MongoDB. Sem auth por padrão até a versão 3.6.", ALTO),
    (5353, "udp"): Servico("mdns", "mDNS", "Descoberta local (Bonjour/Avahi). Multicast 224.0.0.251.", BAIXO),
    (1900, "udp"): Servico("ssdp", "SSDP/UPnP", "Descoberta UPnP. Amplificação DDoS.", ALTO),
    (3260, "tcp"): Servico("iscsi", "iSCSI", "Disco em bloco pela rede.", ALTO),
    (502, "tcp"): Servico("modbus", "Modbus/TCP", "Automação industrial. SEM autenticação por projeto.", ALTO),
    (102, "tcp"): Servico("iso-tsap", "S7comm", "CLPs Siemens S7. Alvo do Stuxnet.", ALTO),
    (20000, "tcp"): Servico("dnp3", "DNP3", "Automação de energia elétrica.", ALTO),
    (44818, "tcp"): Servico("ethernetip", "EtherNet/IP", "Automação Rockwell/Allen-Bradley.", ALTO),
}

# Faixas, para quando o número exato não estiver no catálogo.
FAIXAS = [
    (0, 1023, "Portas de sistema (well-known). Exigem privilégio para escutar no Unix."),
    (1024, 49151, "Portas de usuário (registered). Registráveis na IANA."),
    (49152, 65535, "Portas dinâmicas/efêmeras. Nunca registradas; o cliente pega uma daqui."),
]


def descrever_faixa(porta: int) -> str:
    for ini, fim, texto in FAIXAS:
        if ini <= porta <= fim:
            return texto
    return "Fora da faixa válida (1-65535)."


def consultar(porta: int, protocolo: str) -> Servico | None:
    return CATALOGO.get((porta, protocolo.lower()))


def nome_do_sistema(porta: int, protocolo: str) -> str | None:
    """Consulta o /etc/services do sistema. Pode divergir do catálogo acima:
    o /etc/services é a opinião da distribuição, não a verdade sobre o processo."""
    import socket
    try:
        return socket.getservbyport(porta, protocolo.lower())
    except OSError:
        return None
