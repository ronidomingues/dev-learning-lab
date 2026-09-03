"""Afina (fine-tuning) um BERT em português para triagem de chamados de suporte.

Uso:
    python treinar.py

O script faz, nesta ordem:
  1. carrega o CSV e valida o que veio;
  2. divide em treino/validação/teste de forma ESTRATIFICADA (ver README);
  3. tokeniza;
  4. treina com o `Trainer`;
  5. avalia no conjunto de teste, que o modelo nunca viu;
  6. salva modelo + tokenizador + mapeamento de rótulos em uma pasta só.

Testado em 11/08/2026 com transformers 5.15.0, torch 2.13.0+cpu, datasets 5.0.1.
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from datasets import Dataset
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
    set_seed,
)

from config import config


# --------------------------------------------------------------------------
# 1. Dados
# --------------------------------------------------------------------------
def carregar_dados() -> pd.DataFrame:
    """Lê o CSV e falha cedo, com mensagem útil, se algo estiver errado.

    Validar dados na entrada não é preciosismo: 'acurácia estranha' quase sempre
    nasce de linha vazia, rótulo com espaço sobrando ou classe com 3 exemplos.
    """
    if not config.caminho_dados.exists():
        sys.exit(
            f"ERRO: arquivo de dados não encontrado em {config.caminho_dados}\n"
            f"Defina CAMINHO_DADOS ou rode o script a partir da pasta do projeto."
        )

    df = pd.read_csv(config.caminho_dados)

    faltando = {config.coluna_texto, config.coluna_rotulo} - set(df.columns)
    if faltando:
        sys.exit(f"ERRO: colunas ausentes no CSV: {faltando}. Colunas encontradas: {list(df.columns)}")

    antes = len(df)
    df = df.dropna(subset=[config.coluna_texto, config.coluna_rotulo])
    df[config.coluna_texto] = df[config.coluna_texto].astype(str).str.strip()
    df[config.coluna_rotulo] = df[config.coluna_rotulo].astype(str).str.strip().str.upper()
    df = df[df[config.coluna_texto].str.len() > 0]
    df = df.drop_duplicates(subset=[config.coluna_texto])  # duplicata vaza entre treino e teste
    if len(df) < antes:
        print(f"[dados] {antes - len(df)} linha(s) descartada(s) por vazio/duplicidade")

    contagem = df[config.coluna_rotulo].value_counts()
    print(f"[dados] {len(df)} exemplos, {len(contagem)} classes")
    print(contagem.to_string())

    minimo = contagem.min()
    if minimo < 10:
        print(
            f"AVISO: a classe menos frequente tem só {minimo} exemplos. "
            "Abaixo de ~50 por classe o resultado é instável — ver 75-armadilhas.md"
        )
    return df


def dividir(df: pd.DataFrame):
    """Divide em treino/validação/teste mantendo a proporção das classes.

    Estratificar importa: com divisão aleatória simples e classes desbalanceadas,
    uma classe rara pode sumir do teste e o número final vira ficção.
    """
    rotulos = df[config.coluna_rotulo]
    treino_val, teste = train_test_split(
        df, test_size=config.fracao_teste, stratify=rotulos, random_state=config.semente
    )
    treino, validacao = train_test_split(
        treino_val,
        test_size=config.fracao_validacao,
        stratify=treino_val[config.coluna_rotulo],
        random_state=config.semente,
    )
    print(f"[divisão] treino={len(treino)} validação={len(validacao)} teste={len(teste)}")
    return treino, validacao, teste


# --------------------------------------------------------------------------
# 2. Métricas
# --------------------------------------------------------------------------
def construir_metricas(nomes: list[str]):
    def calcular(pred):
        logits, y_true = pred
        y_pred = np.argmax(logits, axis=-1)
        return {
            "f1_macro": f1_score(y_true, y_pred, average="macro"),
            "acuracia": float((y_pred == y_true).mean()),
        }

    return calcular


# --------------------------------------------------------------------------
# 3. Treino
# --------------------------------------------------------------------------
def main() -> None:
    set_seed(config.semente)  # fixa random, numpy e torch de uma vez

    df = carregar_dados()
    treino_df, val_df, teste_df = dividir(df)

    # Mapeamento rótulo <-> id, ordenado para ser estável entre execuções.
    nomes = sorted(df[config.coluna_rotulo].unique())
    label2id = {nome: i for i, nome in enumerate(nomes)}
    id2label = {i: nome for nome, i in label2id.items()}

    tokenizador = AutoTokenizer.from_pretrained(config.modelo_base)

    def preparar(sub: pd.DataFrame) -> Dataset:
        ds = Dataset.from_dict(
            {
                "text": sub[config.coluna_texto].tolist(),
                "labels": [label2id[r] for r in sub[config.coluna_rotulo]],
            }
        )
        # truncation=True corta o que passa de max_tokens; sem padding aqui —
        # o DataCollator preenche por lote, o que é bem mais rápido.
        return ds.map(
            lambda lote: tokenizador(lote["text"], truncation=True, max_length=config.max_tokens),
            batched=True,
            remove_columns=["text"],
        )

    ds_treino, ds_val, ds_teste = preparar(treino_df), preparar(val_df), preparar(teste_df)

    modelo = AutoModelForSequenceClassification.from_pretrained(
        config.modelo_base,
        num_labels=len(nomes),
        id2label=id2label,
        label2id=label2id,
    )

    import torch  # importado aqui só para detectar acelerador

    tem_cuda = torch.cuda.is_available()

    args = TrainingArguments(
        output_dir=str(config.dir_checkpoints),
        num_train_epochs=config.epocas,
        per_device_train_batch_size=config.lote,
        per_device_eval_batch_size=config.lote * 2,  # avaliação não guarda gradiente
        learning_rate=config.taxa_aprendizado,
        warmup_steps=0.1,          # float < 1 = proporção dos passos (API do transformers 5)
        weight_decay=0.01,
        eval_strategy="epoch",     # no transformers 4.x chamava-se evaluation_strategy
        save_strategy="epoch",
        save_total_limit=1,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        greater_is_better=True,
        logging_steps=10,
        report_to="none",          # sem W&B/TensorBoard; ligue quando quiser rastrear
        seed=config.semente,
        bf16=tem_cuda,             # precisão mista só faz sentido em GPU moderna
    )

    trainer = Trainer(
        model=modelo,
        args=args,
        train_dataset=ds_treino,
        eval_dataset=ds_val,
        processing_class=tokenizador,   # no transformers 4.x era tokenizer=
        data_collator=DataCollatorWithPadding(tokenizador),
        compute_metrics=construir_metricas(nomes),
    )

    print(f"[treino] modelo base: {config.modelo_base} | acelerador: {'GPU' if tem_cuda else 'CPU'}")
    trainer.train()

    # ----------------------------------------------------------------------
    # 4. Avaliação no conjunto de TESTE (nunca usado para escolher nada)
    # ----------------------------------------------------------------------
    saida = trainer.predict(ds_teste)
    y_pred = np.argmax(saida.predictions, axis=-1)
    y_true = np.array(ds_teste["labels"])

    print("\n=== Resultado no conjunto de teste ===")
    print(classification_report(y_true, y_pred, target_names=nomes, digits=3, zero_division=0))
    print("Matriz de confusão (linha = verdadeiro, coluna = previsto)")
    print(pd.DataFrame(confusion_matrix(y_true, y_pred), index=nomes, columns=nomes).to_string())

    # ----------------------------------------------------------------------
    # 5. Salvar tudo que a inferência vai precisar, num lugar só
    # ----------------------------------------------------------------------
    config.dir_saida.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(config.dir_saida))
    tokenizador.save_pretrained(str(config.dir_saida))
    (config.dir_saida / "metricas.json").write_text(
        json.dumps(
            {
                "modelo_base": config.modelo_base,
                "f1_macro_teste": float(f1_score(y_true, y_pred, average="macro")),
                "acuracia_teste": float((y_pred == y_true).mean()),
                "n_treino": len(treino_df),
                "n_teste": len(teste_df),
                "epocas": config.epocas,
                "taxa_aprendizado": config.taxa_aprendizado,
                "semente": config.semente,
                "rotulos": nomes,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"\n[ok] modelo salvo em {config.dir_saida}")
    print("     próximo passo:  python prever.py \"minha fatura veio errada\"")


if __name__ == "__main__":
    main()
