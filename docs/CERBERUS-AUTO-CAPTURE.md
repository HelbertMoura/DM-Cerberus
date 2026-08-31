# Cerberus Auto Capture

Fontes aceitas: relatórios de TASK/QA/RCA, handovers aprovados, ADRs aprovadas e eventos aceitos do orquestrador. Chats brutos não são fonte automática.

`cerberus ingest-report <arquivo> --task <id> --project <id> --agent <papel>` extrai bullets de seções Learnings/Lições/Gotchas/Findings e cria candidatos. Duplicatas exatas são eliminadas por fingerprint. Conteúdo suspeito de segredo é redigido e marcado `QUARANTINED`.

Watcher contínuo não está habilitado neste hardening. A alimentação automática deve ser acionada por job incremental ou evento `REPORT_ACCEPTED`, preservando o boundary e sem alterar a state machine do orquestrador.
