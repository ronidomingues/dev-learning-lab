import { LightningElement, api, wire } from 'lwc';
import { refreshApex } from '@salesforce/apex';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';
import listarPorEquipamento from '@salesforce/apex/OrdemServicoService.listarPorEquipamento';
import concluirDoPainel from '@salesforce/apex/OrdemServicoService.concluirDoPainel';

const COLUNAS = [
    { label: 'OS', fieldName: 'link', type: 'url', initialWidth: 110,
      typeAttributes: { label: { fieldName: 'Name' }, target: '_self' } },
    { label: 'Status', fieldName: 'Status__c', initialWidth: 120 },
    { label: 'Prioridade', fieldName: 'Prioridade__c', initialWidth: 110 },
    { label: 'Abertura', fieldName: 'Abertura__c', type: 'date',
      typeAttributes: { day: '2-digit', month: '2-digit', year: 'numeric',
                        hour: '2-digit', minute: '2-digit' } },
    { label: 'SLA (h)', fieldName: 'SLA_Horas__c', type: 'number', initialWidth: 90,
      cellAttributes: { alignment: 'center' } },
    { label: 'Dentro do SLA', fieldName: 'Dentro_SLA__c', type: 'boolean', initialWidth: 130,
      cellAttributes: { alignment: 'center' } },
    { label: 'Horas', fieldName: 'Horas_Gastas__c', type: 'number', initialWidth: 90 },
    { type: 'action', typeAttributes: { rowActions: { fieldName: 'acoes' } } }
];

const ACOES_ABERTA = [{ label: 'Concluir', name: 'concluir' }];
const ACOES_FECHADA = [{ label: 'Abrir registro', name: 'abrir' }];

export default class PainelOrdens extends LightningElement {
    /** Preenchido automaticamente quando o componente está numa página de registro. */
    @api recordId;

    /** Propriedade de design: configurável no App Builder (ver .js-meta.xml). */
    @api apenasAbertas = false;

    colunas = COLUNAS;
    carregando = false;
    mostrarModal = false;
    ordemSelecionada = null;
    horas = 1;

    /**
     * Guardamos o resultado bruto do @wire para poder chamar refreshApex depois.
     * Sem isso, a tabela não atualiza após concluir — o cache do Lightning Data
     * Service devolve o valor antigo. É a pegadinha nº 1 de LWC com Apex.
     */
    resultadoWire;

    @wire(listarPorEquipamento, {
        equipamentoId: '$recordId',
        apenasAbertas: '$apenasAbertas'
    })
    receberOrdens(resultado) {
        this.resultadoWire = resultado;
    }

    /** Adapta os dados do Apex para o formato que a datatable espera. */
    get linhas() {
        const dados = this.resultadoWire?.data;
        if (!dados) {
            return [];
        }
        const terminais = ['Concluida', 'Cancelada'];
        return dados.map((os) => ({
            ...os,
            link: `/lightning/r/Ordem_Servico__c/${os.Id}/view`,
            acoes: terminais.includes(os.Status__c) ? ACOES_FECHADA : ACOES_ABERTA
        }));
    }

    get temErro() {
        return this.resultadoWire?.error !== undefined;
    }

    get mensagemErro() {
        return this.resultadoWire?.error?.body?.message ?? 'Erro ao carregar as ordens.';
    }

    get vazio() {
        return !this.temErro && this.linhas.length === 0;
    }

    get titulo() {
        const n = this.linhas.length;
        return `Ordens de serviço (${n})`;
    }

    get horasInvalidas() {
        const h = parseFloat(this.horas);
        return Number.isNaN(h) || h <= 0 || h > 24;
    }

    handleRowAction(evento) {
        const acao = evento.detail.action.name;
        const linha = evento.detail.row;

        if (acao === 'concluir') {
            this.ordemSelecionada = linha;
            this.horas = 1;
            this.mostrarModal = true;
        } else {
            window.open(linha.link, '_self');
        }
    }

    handleHoras(evento) {
        this.horas = evento.target.value;
    }

    fecharModal() {
        this.mostrarModal = false;
        this.ordemSelecionada = null;
    }

    async confirmarConclusao() {
        if (this.horasInvalidas) {
            this.toast('Valor inválido', 'Informe entre 0,5 e 24 horas.', 'warning');
            return;
        }

        // Guarda contra duplo clique: sem isto o usuário conclui a mesma OS duas vezes.
        this.carregando = true;
        try {
            const mensagem = await concluirDoPainel({
                ordemId: this.ordemSelecionada.Id,
                horas: parseFloat(this.horas)
            });
            this.toast('Pronto', mensagem, 'success');
            this.fecharModal();
            // Invalida o cache do @wire e recarrega a tabela.
            await refreshApex(this.resultadoWire);
        } catch (erro) {
            const msg = erro?.body?.message ?? erro?.message ?? 'Erro desconhecido.';
            this.toast('Não foi possível concluir', msg, 'error', 'sticky');
        } finally {
            this.carregando = false;
        }
    }

    toast(title, message, variant, mode = 'dismissable') {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant, mode }));
    }
}
