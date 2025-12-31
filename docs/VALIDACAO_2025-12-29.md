# 📊 Validação TXT vs XML — 29/12/2025

**TXTs validados:** 613  
**Mapas OK (100%):** 390  
**Mapas com divergência:** 198  
**XML não encontrados:** 25  
**Relatório detalhado:** `/mnt/c/prd_debian/VALIDACAO_TXT_vs_XML.md`

---

## Panorama
- **Aderência**: 390 mapas bateram 100% entre TXT e XML usado na validação.  
- **Divergência**: 198 mapas com diferenças de produtos/quantidades; 25 deles nem tiveram XML localizado.  
- **Principal fator**: muitos TXTs foram confrontados com XML `ocp_*.xml` em `mapas_xml_saidas*` (saída de outro fluxo/versão), não com os XML originais de entrada.

---

## 🟢 Mapas OK (390)
390 mapas com correspondência completa TXT ↔ XML de referência.

---

## 🔴 Mapas com divergência (198)
- **Motivo**: para esses mapas, o TXT foi confrontado com XML `ocp_*.xml` de `mapas_xml_saidas*` (arquivos de saída), que têm SKUs/quantidades diferentes dos XML de entrada. Por isso surgem produtos faltantes/excedentes e diferenças de quantidade.  
- **XML ausente**: 25 mapas entram como divergentes porque nenhum XML foi encontrado.  
- **Detalhamento**: lista completa de mapas, SKUs faltantes/excedentes e diferenças de quantidade em `/mnt/c/prd_debian/VALIDACAO_TXT_vs_XML.md`.

---

## Nota técnica
Para validar contra o que foi realmente processado, o ideal é priorizar `meus_xmls` no `validar_txt_vs_xml.py` (ou excluir `mapas_xml_saidas*` da busca), evitando comparar TXTs com XML de outro fluxo.
