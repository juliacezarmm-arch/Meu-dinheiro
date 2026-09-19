# Meu Dinheiro

Aplicativo de organização financeira pessoal para registrar entradas, saídas, cartão de crédito, investimentos e metas, com saldo disponível calculado a partir do saldo inicial.

## Como utilizar

1. Se já utiliza o aplicativo, abra primeiro seu arquivo JSON de dados. Guarde uma cópia de segurança usando **Salvar como** antes de atualizar lançamentos antigos.
2. No **Extrato**, informe o saldo que realmente está disponível no momento da abertura, sem contar valores já investidos ou reservados em metas.
3. Registre recebimentos e despesas realizados. Compras no crédito são previstas na aba **Cartão**; use **Registrar pagamento** na fatura correspondente para descontar o dinheiro disponível, inclusive nos pagamentos parciais.
4. Nos cartões já cadastrados, configure o dia de fechamento. Faturas anteriores à data do saldo inicial não são conciliadas automaticamente.
5. Use **Salvar** ou **Salvar como** para guardar os dados no computador. Publicar o código no GitHub não guarda seus lançamentos pessoais.

## Revisão de integridade (setembro de 2026)

A revisão corrige a inclusão de lançamentos futuros no saldo de abertura, classificação de resgates como receitas, centavos em compras parceladas, vínculo dos pagamentos às faturas, proteção dos valores reservados em metas, validação do arquivo JSON e exibição segura de textos cadastrados. O saldo do cabeçalho é o disponível **hoje**, independentemente do mês escolhido nos relatórios. Os indicadores percentuais de investimentos continuam aproximados, não uma medida de rentabilidade ponderada pelo tempo.

Testes automatizados estão em `tests/finance.test.js` e no fluxo `.github/workflows/verificar-financas.yml`. Eles não substituem a conferência dos resultados com seu extrato bancário real.
