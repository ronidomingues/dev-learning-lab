"""cofrelib — criptografia de arquivos em Python puro, para estudo.

Módulos, na ordem em que vale a pena lê-los:

    chacha20.py   cifra de fluxo (sigilo)
    poly1305.py   autenticador de uso único (integridade)
    aead.py       os dois combinados, do jeito certo (RFC 8439)
    x25519.py     Diffie-Hellman em curva elíptica (acordo de chaves)
    kdf.py        scrypt (senha -> chave) e HKDF (segredo -> chaves)
    chaves.py     arquivos de chave e permissões
    formato.py    formato de arquivo versionado e autenticado
    cli.py        interface de linha de comando

NÃO USE ESTE PACOTE EM PRODUÇÃO. Ele é correto quanto aos vetores de teste
oficiais, e deliberadamente ingênuo quanto a canais laterais (tempo, cache,
memória). Em produção: libsodium, a biblioteca `cryptography`, ou `age`.
"""

VERSAO = "1.0.0"
