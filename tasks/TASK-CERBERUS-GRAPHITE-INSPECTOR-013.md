# TASK-CERBERUS-GRAPHITE-INSPECTOR-013

Status: implementação validada; conferência visual no navegador pendente por permissão recusada.

## Objetivo

Revisar as novas medições de uso e reformular o Inspector e login em grafite e verde discreto,
usando saiforanocode e preservando a memória sob demanda.

## Entrega

- Navegação lateral, visão geral inicial, tabelas planas e login consistente.
- Filtros temporais, CSV protegido, feedback de erro, proteção contra respostas atrasadas.
- IDs duplicados, consulta repetida e cobertura artificial corrigidos.
- Configurador local de senha via getpass, hashes, backup e preservação de 2FA e outras contas.
- Ledger normalizado: idempotência, campos desconhecidos nulos, totals parciais e reasoning sem dupla contagem.
- Custos sem tarifa configurada indisponíveis; radar apresentado como não conectado às leituras produtivas.
- Encerramento do painel confere a identidade do processo antes de pará-lo.

## Validação

177 testes combinados, OK, sem skips; verificações focais posteriores também passaram.
QA independente PASS para ledger/HTTP e interface/configurador. Contraste dos campos calculado >=3:1.
Servidor local recarregado sem abrir navegador, health HTTP 200, bind 127.0.0.1:8765.

## Limites

Sem validação de renderização no navegador porque o acesso foi recusado. Telemetria depende de counters
disponíveis nos payloads. Sem integração com cota oficial e sem prevenção produtiva de loops.
Fingerprint de evento sem identidade da origem pode confundir turnos legítimos idênticos.

Próximo passo: usuário definir a senha localmente se necessário e conferir a interface no navegador.
