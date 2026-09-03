import { test } from "node:test";
import assert from "node:assert/strict";
import { validarDestino, validarSlug, ehHostPrivado } from "../src/validate.js";

test("aceita http e https", () => {
  assert.equal(validarDestino("https://exemplo.com/a"), "https://exemplo.com/a");
  assert.ok(validarDestino("http://exemplo.com").startsWith("http://"));
});

test("rejeita esquemas perigosos", () => {
  for (const mau of ["javascript:alert(1)", "data:text/html,<script>", "file:///etc/passwd"]) {
    assert.throws(() => validarDestino(mau), /http ou https|URL válida/);
  }
});

test("rejeita destino vazio, nulo e não string", () => {
  for (const mau of ["", "   ", null, undefined, 42, {}]) {
    assert.throws(() => validarDestino(mau), /obrigatório|válida/);
  }
});

test("rejeita destino maior que 2048 caracteres", () => {
  assert.throws(() => validarDestino("https://x.com/" + "a".repeat(2100)), /2048/);
});

test("bloqueia SSRF para endereços privados e metadados de nuvem", () => {
  for (const host of ["http://localhost:8080", "http://127.0.0.1", "http://10.0.0.5",
                      "http://192.168.1.1", "http://172.16.0.9", "http://169.254.169.254/latest/meta-data/"]) {
    assert.throws(() => validarDestino(host), /privado ou local/, `deveria bloquear ${host}`);
  }
});

test("ehHostPrivado reconhece a faixa 172.16–172.31 e não a 172.32", () => {
  assert.equal(ehHostPrivado("172.16.0.1"), true);
  assert.equal(ehHostPrivado("172.31.255.255"), true);
  assert.equal(ehHostPrivado("172.32.0.1"), false);
});

test("valida apelido: tamanho, alfabeto e palavras reservadas", () => {
  assert.equal(validarSlug("meuLink"), "meuLink");
  assert.throws(() => validarSlug("ab"), /3 a 32/);
  assert.throws(() => validarSlug("com espaco"), /não permitido/);
  assert.throws(() => validarSlug("com-hifen"), /não permitido/);
  assert.throws(() => validarSlug("api"), /reservado/);
  assert.throws(() => validarSlug("HEALTH"), /reservado/);
});
