---
titulo: Integração SEFAZ Nacional & Certificados A1
tags: [fiscal, sefaz, nfe, certificado-a1, pki]
atualizado: 2026-08-22
status: ativo
---

# 🔐 Fiscal: Integração SEFAZ Nacional & Certificados A1
> **Ambiente:** SEFAZ Ambiente Nacional / Distribuição DF-e (NFeDistribuicaoDFe)
> **CNPJ Construtora Teenus:** `19.206.579/0001-71`

---

## 🔑 Especificação Técnica do Certificado Digital A1
- **Formato:** PKCS#12 (`.pfx` / `.p12`)
- **Segurança:** Criptografia simétrica AES-256 no banco de dados com chave de cofre restrita por tenant.
- **Assinatura:** Padrão XMLDSig (RSA-SHA1 / RSA-SHA256) com canonicidade C14N.
- **Comunicação:** Handshake mTLS (Mutual TLS) com a SEFAZ Nacional via SOAP 1.2.
