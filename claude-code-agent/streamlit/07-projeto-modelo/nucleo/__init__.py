"""Núcleo da aplicação: regras de negócio e acesso a dados.

REGRA DE OURO DESTE PACOTE: nenhum arquivo aqui importa `streamlit`.
É isso que permite testar o backend com pytest puro, reaproveitar o mesmo
código numa API FastAPI ou num job agendado, e trocar a interface um dia
sem reescrever a lógica.
"""
