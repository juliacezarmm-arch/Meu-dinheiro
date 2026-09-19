# Cadastro de recorrências — escopo aprovado em 19/09/2026

Cadastro único no Extrato com atalho na aba Cartão, contemplando salário, débito automático, gastos e assinaturas no cartão. Informações: nome, tipo (entrada/saída), valor, categoria, subcategoria, meio de pagamento, cartão quando aplicável, frequência semanal/mensal/anual, data da primeira ocorrência e data opcional de encerramento. Permitir edição, cancelamento e exclusão do agendamento preservando lançamentos históricos.

O usuário não precisa classificar manualmente lançamentos como fixos ou variáveis: agendamentos são recorrentes; lançamentos avulsos são avulsos. Dados legados não devem ser excluídos nem mudar de valor.

A programação é distinta do fato financeiro. Ocorrências futuras aparecem como previstas, sem alterar caixa. Quando a data chega, o aplicativo gera um lançamento apenas uma vez (identificador estável de recorrência/data), deixando claro que não verifica a conta bancária. Para cartão gera compra no cartão, não lançamento extra no extrato; faturas continuam reduzindo caixa somente quando registradas como pagas. Ocorrências anteriores ao saldo inicial não devem gerar novas entradas/saídas retroativas; registros antigos continuam preservados. Ao cancelar, não gerar novas ocorrências a partir da data de cancelamento, sem apagar meses anteriores.

Não utilizar alertas, prompts ou confirmações nativas do navegador. Preservar JSON, IndexedDB e autossalvamento já implementados. Validar e testar antes de publicar.
