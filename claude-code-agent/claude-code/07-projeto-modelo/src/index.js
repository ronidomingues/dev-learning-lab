// Ponto de entrada. Configuração vem do ambiente, com padrão seguro.
import { criarServidor } from './servidor.js';

const porta = Number(process.env.PORTA ?? 3000);
const servidor = criarServidor();

servidor.listen(porta, () => {
  console.log(`servidor de tarefas ouvindo em http://localhost:${porta}`);
});

// Desligamento gracioso: sem isso, Ctrl+C derruba conexões no meio.
for (const sinal of ['SIGINT', 'SIGTERM']) {
  process.on(sinal, () => {
    console.log(`\nrecebido ${sinal}, encerrando...`);
    servidor.close(() => process.exit(0));
  });
}
