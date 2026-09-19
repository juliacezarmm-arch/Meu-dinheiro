# Padrão de interface para os aplicativos da Julia

**Regra de experiência do usuário:** não utilizar caixas de diálogo nativas do navegador (`window.alert`, `window.confirm`, `window.prompt`) para mensagens, edição, confirmação ou registro. Desenvolver componentes visuais integrados ao próprio site, coerentes com o tema, acessíveis por teclado, com rótulos claros, validações e ações de salvar/cancelar. Utilizar ícone de lápis para editar registros e evitar solicitações de configuração que confundam conceitos distintos.

**Exceção técnica:** o seletor de arquivos do sistema operacional para abrir/salvar dados é necessário e não é uma notificação. Ao fechar a aba, o navegador não permite substituição confiável da confirmação nativa por um modal próprio; preferir indicador persistente de alterações não salvas e salvamento automático quando houver permissão sobre arquivo.

**Cartão de crédito:** data de compra, data de vencimento da fatura e data efetiva do pagamento são conceitos separados. Dia habitual de pagamento é referência opcional, não comprovação de pagamento. Mudanças cadastrais não reescrevem compras antigas nem pagamentos vinculados. Preservar o marco zero definido pelo saldo inicial.

Reutilizar este padrão em outros projetos e aplicativos desenvolvidos com a usuária.