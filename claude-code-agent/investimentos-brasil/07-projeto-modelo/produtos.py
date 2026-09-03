"""
produtos.py — modelos dos produtos de renda fixa disponiveis ao varejo.

Cada produto sabe: quanto rende bruto, que custo cobra, que imposto paga e
que garantia tem. O objetivo do modulo e permitir a UNICA comparacao que
importa: quanto sobra no seu bolso, no seu prazo.

Convencao de taxas: CDI, Selic, prefixado e IPCA+ sao cotados em base
252 dias uteis. Convertemos dias corridos em uteis pela razao media
252/365. E uma aproximacao (ignora feriados especificos do periodo) e a
diferenca contra o calculo exato da B3 fica na terceira casa decimal.
"""

from dataclasses import dataclass, field

import indicadores as ind
import tributos as trib


# --- conversao de taxas ----------------------------------------------------

def fator_periodo(taxa_aa: float, dias_corridos: int, base: int = 252) -> float:
    """Fator multiplicativo de uma taxa anual num periodo de dias corridos."""
    if dias_corridos < 0:
        raise ValueError("dias_corridos nao pode ser negativo")
    if base == 252:
        dias_uteis = dias_corridos * ind.DIAS_UTEIS_ANO / ind.DIAS_CORRIDOS_ANO
        return (1 + taxa_aa) ** (dias_uteis / ind.DIAS_UTEIS_ANO)
    return (1 + taxa_aa) ** (dias_corridos / ind.DIAS_CORRIDOS_ANO)


def anualizar(fator: float, dias_corridos: int) -> float:
    """Converte um fator acumulado em taxa equivalente ao ano."""
    if dias_corridos <= 0:
        raise ValueError("dias_corridos deve ser positivo")
    return fator ** (ind.DIAS_CORRIDOS_ANO / dias_corridos) - 1


# --- resultado -------------------------------------------------------------

@dataclass(frozen=True)
class Resultado:
    produto: str
    principal: float
    dias: int
    bruto: float          # rendimento bruto em R$
    iof: float
    ir: float
    taxas: float          # custodia, administracao, corretagem
    liquido: float        # rendimento liquido em R$
    observacao: str = ""

    @property
    def valor_final(self) -> float:
        return self.principal + self.liquido

    @property
    def taxa_liquida_aa(self) -> float:
        return anualizar(self.valor_final / self.principal, self.dias)

    @property
    def taxa_real_aa(self) -> float:
        return ind.juro_real(self.taxa_liquida_aa)


# --- produtos --------------------------------------------------------------

@dataclass
class Produto:
    nome: str
    garantia: str = "nenhuma"
    liquidez: str = "diaria"
    isento_ir: bool = False
    carencia_dias: int = 0
    risco: str = "baixo"

    def taxa_bruta_aa(self) -> float:
        raise NotImplementedError

    def custos(self, principal: float, dias: int) -> float:
        return 0.0

    def simular(self, principal: float, dias: int) -> Resultado:
        if principal <= 0:
            raise ValueError("principal deve ser positivo")
        if dias <= 0:
            raise ValueError("dias deve ser positivo")
        obs = ""
        if dias < self.carencia_dias:
            obs = f"RESGATE BLOQUEADO: carencia de {self.carencia_dias} dias"
        bruto = principal * (fator_periodo(self.taxa_bruta_aa(), dias) - 1)
        custo = self.custos(principal, dias)
        base = bruto - custo
        imp_iof = trib.iof(base, dias)
        imp_ir = trib.imposto_renda(base, dias, isento=self.isento_ir)
        liq = base - imp_iof - imp_ir
        return Resultado(self.nome, principal, dias, bruto, imp_iof, imp_ir,
                         custo, liq, obs)


@dataclass
class Poupanca(Produto):
    nome: str = "Poupanca"
    garantia: str = "FGC ate R$ 250 mil"
    isento_ir: bool = True

    def taxa_bruta_aa(self) -> float:
        return (1 + ind.poupanca_mensal()) ** 12 - 1

    def simular(self, principal: float, dias: int) -> Resultado:
        """A poupanca so credita no ANIVERSARIO mensal.

        Resgatar no dia 29 do mes perde o rendimento inteiro daquele mes.
        Modelamos isso: so contam os meses cheios.
        """
        meses = dias // 30
        fator = (1 + ind.poupanca_mensal()) ** meses
        bruto = principal * (fator - 1)
        obs = "" if meses else "menos de um mes: rendimento zero (aniversario mensal)"
        return Resultado(self.nome, principal, dias, bruto, 0.0, 0.0, 0.0, bruto, obs)


@dataclass
class PosFixadoCDI(Produto):
    """CDB, LCI, LCA, RDB e afins indexados ao CDI."""
    nome: str = "CDB 100% CDI"
    percentual_cdi: float = 1.00
    garantia: str = "FGC ate R$ 250 mil"

    def taxa_bruta_aa(self) -> float:
        """Aproximacao de mercado: 'X% do CDI' multiplica a taxa, nao o fator.

        A convencao exata da B3 aplica o percentual ao fator DIARIO. A
        diferenca contra esta aproximacao aparece na terceira casa decimal.
        """
        return ind.CDI * self.percentual_cdi


@dataclass
class TesouroSelic(Produto):
    nome: str = "Tesouro Selic"
    agio_aa: float = 0.0004          # o "Selic + 0,04%" que aparece na tela
    garantia: str = "Tesouro Nacional (risco soberano)"
    isencao_custodia: float = ind.ISENCAO_CUSTODIA_TESOURO_SELIC

    def taxa_bruta_aa(self) -> float:
        return ind.SELIC_OVER + self.agio_aa

    def custos(self, principal: float, dias: int) -> float:
        """Custodia da B3: 0,20% a.a. so sobre o que exceder a isencao."""
        base = max(0.0, principal - self.isencao_custodia)
        return base * ind.TAXA_CUSTODIA_B3 * dias / ind.DIAS_CORRIDOS_ANO


@dataclass
class TesouroReserva(TesouroSelic):
    """Titulo lancado em 11/05/2026: 100% da Selic, 24x7, sem marcacao a mercado."""
    nome: str = "Tesouro Reserva"
    agio_aa: float = 0.0
    isencao_custodia: float = float("inf")   # ver README: confirmar na sua instituicao


@dataclass
class Prefixado(Produto):
    nome: str = "Tesouro Prefixado"
    taxa_aa: float = 0.1400
    garantia: str = "Tesouro Nacional (risco soberano)"
    liquidez: str = "diaria com marcacao a mercado"
    risco: str = "medio (oscila antes do vencimento)"

    def taxa_bruta_aa(self) -> float:
        return self.taxa_aa

    def custos(self, principal: float, dias: int) -> float:
        return principal * ind.TAXA_CUSTODIA_B3 * dias / ind.DIAS_CORRIDOS_ANO


@dataclass
class IPCAMais(Produto):
    nome: str = "Tesouro IPCA+"
    taxa_real_aa: float = 0.0665
    inflacao_esperada: float = ind.IPCA_ESPERADO
    garantia: str = "Tesouro Nacional (risco soberano)"
    liquidez: str = "diaria com marcacao a mercado"
    risco: str = "medio (oscila antes do vencimento)"

    def taxa_bruta_aa(self) -> float:
        """Taxa nominal = (1 + real) * (1 + inflacao) - 1. Nunca a soma."""
        return (1 + self.taxa_real_aa) * (1 + self.inflacao_esperada) - 1

    def custos(self, principal: float, dias: int) -> float:
        return principal * ind.TAXA_CUSTODIA_B3 * dias / ind.DIAS_CORRIDOS_ANO


@dataclass
class FundoDI(Produto):
    """Fundo referenciado DI: come-cotas semestral + taxa de administracao."""
    nome: str = "Fundo DI (0,50% a.a.)"
    taxa_admin_aa: float = 0.0050
    percentual_cdi: float = 1.00
    garantia: str = "nenhuma (patrimonio segregado, sem FGC)"
    longo_prazo: bool = True

    def taxa_bruta_aa(self) -> float:
        bruta = ind.CDI * self.percentual_cdi
        return (1 + bruta) / (1 + self.taxa_admin_aa) - 1

    def simular(self, principal: float, dias: int) -> Resultado:
        aliq_cc = (trib.ALIQUOTA_COME_COTAS_LONGO if self.longo_prazo
                   else trib.ALIQUOTA_COME_COTAS_CURTO)
        capital = principal
        ganho_total = 0.0
        ir_pago = 0.0
        decorridos = 0
        while decorridos + 182 <= dias:
            novo = capital * fator_periodo(self.taxa_bruta_aa(), 182)
            ganho = novo - capital
            ganho_total += ganho
            imposto = ganho * aliq_cc          # come-cotas: sai em cotas
            capital = novo - imposto
            ir_pago += imposto
            decorridos += 182
        resto = dias - decorridos
        if resto:
            novo = capital * fator_periodo(self.taxa_bruta_aa(), resto)
            ganho_total += novo - capital
            capital = novo
        devido = trib.aliquota_ir(dias) * ganho_total
        complemento = max(0.0, devido - ir_pago)
        capital -= complemento
        bruto_sem_admin = principal * (fator_periodo(ind.CDI * self.percentual_cdi, dias) - 1)
        taxa_admin = bruto_sem_admin - ganho_total
        obs = f"{trib.datas_come_cotas(dias)} evento(s) de come-cotas"
        return Resultado(self.nome, principal, dias, bruto_sem_admin, 0.0,
                         ir_pago + complemento, max(0.0, taxa_admin),
                         capital - principal, obs)


def catalogo() -> list:
    """A prateleira que um investidor de varejo realmente encontra em 2026."""
    return [
        Poupanca(),
        TesouroReserva(),
        TesouroSelic(),
        PosFixadoCDI(nome="CDB 100% CDI (banco grande)", percentual_cdi=1.00),
        PosFixadoCDI(nome="CDB 110% CDI (banco medio)", percentual_cdi=1.10),
        PosFixadoCDI(nome="CDB 120% CDI (banco pequeno)", percentual_cdi=1.20,
                     liquidez="no vencimento", carencia_dias=720,
                     risco="credito do emissor; FGC cobre ate R$ 250 mil"),
        PosFixadoCDI(nome="LCI/LCA 88% CDI (isenta de IR)", percentual_cdi=0.88,
                     isento_ir=True, carencia_dias=180,
                     liquidez="apos 6 meses de carencia"),
        FundoDI(nome="Fundo DI (0,50% a.a.)", taxa_admin_aa=0.0050),
        FundoDI(nome="Fundo DI caro (2,00% a.a.)", taxa_admin_aa=0.0200),
        Prefixado(nome="Tesouro Prefixado 2029 (14,20%)", taxa_aa=0.1420,
                  liquidez="diaria com marcacao a mercado"),
        IPCAMais(nome="Tesouro IPCA+ 2035 (IPCA+6,65%)", taxa_real_aa=0.0665),
    ]
