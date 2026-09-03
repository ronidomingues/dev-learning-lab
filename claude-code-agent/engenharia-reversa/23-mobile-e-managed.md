# 23 · Mobile e código gerenciado (Android, iOS, .NET, Java)

**Nível:** avançado · **Data:** 03/09/2026

Nem todo binário é código de máquina. **Código gerenciado** (Java/Kotlin no Android, C#/.NET,
Python) roda sobre uma máquina virtual e carrega **muito mais metadados** — o que torna a
descompilação quase um retorno ao fonte. Este arquivo cobre esse mundo e o RE de apps móveis,
onde a instrumentação dinâmica (Frida) reina.

---

## 1. Por que gerenciado é mais fácil de reverter

Bytecode de VM (Java `.class`/DEX, .NET CIL) preserva **nomes de classes, métodos, campos e
tipos** — o compilador precisa deles para *linking* e reflexão em runtime. Resultado:
descompiladores de Java/.NET produzem código quase idêntico ao original. Por isso:
- **Ofuscadores comerciais existem** justamente para essas plataformas (ProGuard/R8,
  DexGuard, Dotfuscator) — sem eles, o código está às claras.
- A defesa real de segredos continua sendo **não colocá-los no cliente**.

---

## 2. Android — APK, DEX e o fluxo de RE

Um **APK** é um ZIP: `classes.dex` (bytecode Dalvik/ART), `AndroidManifest.xml`, `resources`,
`lib/` (bibliotecas nativas `.so` por arquitetura), assinaturas.

```bash
unzip -l app.apk                 # ver o conteúdo
```

### Ferramentas
| Ferramenta | Faz |
|---|---|
| **jadx / jadx-gui** | DEX → **Java** legível. A primeira parada. `jadx -d saida app.apk` |
| **apktool** | Desmonta para **smali** (assembly Dalvik) e **remonta** o APK (para patching) |
| **Ghidra/IDA** | Reverter as libs **nativas** (`lib/arm64-v8a/*.so`) — o C/C++ do app |
| **Frida / Objection** | Instrumentação dinâmica: hooks em métodos Java e nativos, ao vivo |
| **Burp/mitmproxy** | Interceptar o tráfego (requer contornar *cert pinning*) |

### Fluxo típico
1. `jadx-gui app.apk` → leia o `AndroidManifest.xml` (permissões, componentes exportados,
   `MainActivity`), depois a lógica em Java.
2. Achou uma checagem (root/licença/pin)? **Frida** para contorná-la em runtime, ou **apktool**
   para patchar o smali e reempacotar (`apktool b` + assinar com `apksigner`).
3. Lógica sensível costuma estar nas **libs nativas** (`.so`) para dificultar — reverta com
   Ghidra e/ou Frida (`Interceptor` em exports nativos).

### Contornar cert pinning (pentest autorizado)
Apps validam o certificado do servidor para impedir interceptação. Com Frida/Objection você
força as funções de validação a aceitarem seu proxy — passo padrão para auditar o tráfego de
um app **em teste autorizado**.

---

## 3. iOS — o essencial

- **`.ipa`** é um ZIP com o app Mach-O (ARM64) + recursos. Apps da App Store vêm **cifrados**
  (FairPlay); é preciso um dispositivo com jailbreak e ferramentas (frida-ios-dump, decrypt em
  memória) para obter o binário em claro.
- Reversão do Mach-O no Ghidra/IDA/**Hopper**; metadados Objective-C/Swift ajudam bastante
  ([`13-formatos-de-binario.md`](13-formatos-de-binario.md)).
- **Frida** domina o dinâmico (hooks em Objective-C via `ObjC.classes`, e em Swift/nativo).
- Restrições da plataforma (assinatura de código, sandbox) tornam o dinâmico mais burocrático
  que no Android.

---

## 4. .NET (C#, VB.NET) — quase o fonte de volta

O .NET compila para **CIL** (bytecode) num assembly PE (`.exe`/`.dll`). Descompiladores
reconstroem C# muito fiel:
| Ferramenta | Faz |
|---|---|
| **ILSpy** | Descompila para C# (multiplataforma, grátis) |
| **dnSpy / dnSpyEx** | Descompila **e edita e depura** .NET — patcha e salva o assembly |
| **de4dot** | Remove ofuscação comum de .NET |

Com **dnSpy** você abre um `.exe`, edita um método (ex.: `return true` numa checagem de
licença), e salva o binário modificado — RE e patching numa ferramenta só. Ofuscadores (.NET
Reactor, etc.) elevam o custo; `de4dot` desfaz muitos.

---

## 5. Java (desktop/servidor) e outros bytecodes

- **Java `.jar`/`.class`:** descompiladores como **CFR**, **Procyon**, **Fernflower** (o do
  IntelliJ) reconstroem Java legível. Ofuscação (nomes `a.a.a`) é a principal barreira.
- **Python `.pyc`:** **decompyle3/uncompyle6** recuperam o `.py` (com limites por versão).
  Apps "empacotados" com PyInstaller podem ser **desempacotados** (`pyinstxtractor`) para obter
  os `.pyc`.
- **WebAssembly (`.wasm`):** `wasm-decompile` (WABT), `wasm2c`, ou Ghidra. Cada vez mais comum
  em apps web e alvo emergente de RE ([`65-estado-da-arte.md`](65-estado-da-arte.md)).

---

## 6. Frida no centro do RE mobile

A instrumentação dinâmica é tão central em mobile que merece destaque. Padrões de uso:
```javascript
// Android: hookar um método Java (ex.: uma checagem de root que retorna boolean)
Java.perform(() => {
  const Sec = Java.use('com.app.Security');
  Sec.isRooted.implementation = function () {
    console.log('isRooted() chamado -> retornando false');
    return false;
  };
});
```
Com isso você contorna checagens sem tocar o APK. **Objection** empacota dezenas desses truques
(bypass de pinning, de root, dump de memória) em comandos prontos. Requer `frida-server` no
dispositivo (ou *gadget* embutido no app repackaged) — e apps podem detectar/impedir Frida
([`19-anti-analise.md`](19-anti-analise.md)).

---

## 7. Ética e legalidade

- Reverter **seu** app, ou sob **contrato de pentest**/programa de bug bounty: legítimo.
- Reverter apps de terceiros para pirataria, remoção de anúncios/licença, ou para fraudar
  (cheating, in-app purchase) viola a EULA, direitos autorais e pode ser crime.
- **Interoperabilidade e pesquisa de segurança** têm proteções (variáveis por país). No Brasil,
  a Lei do Software é omissa sobre RE; a Lei 12.737/2012 pune acesso não autorizado a
  dispositivos. Trate dispositivos e contas alheias como fora dos limites sem autorização.

---

## Autoteste

1. Por que descompilar um app Android/.NET chega mais perto do fonte que um binário C?
2. Descreva o fluxo de RE de um APK: do ZIP ao contorno de uma checagem, citando as ferramentas.
3. Qual a diferença entre usar **apktool** (smali) e **Frida** para contornar uma verificação?
4. Por que apps iOS da App Store precisam ser "decifrados" antes de reverter, e como se faz?
5. O que **dnSpy** permite que um descompilador comum de .NET (como ILSpy) não permite?
6. Escreva um hook Frida que força um método Java `isRooted()` a retornar `false`.
7. Onde estão os limites éticos/legais ao reverter um app de terceiros?
