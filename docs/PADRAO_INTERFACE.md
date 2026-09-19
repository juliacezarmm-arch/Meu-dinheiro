# Padrão de interface para os aplicativos da Julia

**Regra de experiência do usuário:** não utilizar caixas de diálogo nativas do navegador (`window.alert`, `window.confirm`, `window.prompt`) para mensagens, edição, confirmação ou registro. Desenvolver componentes visuais integrados ao próprio site, coerentes com o tema, acessíveis por teclado, com rótulos claros, validações e ações de salvar/cancelar. Utilizar ícone de lápis para editar registros e evitar solicitações de configuração que confundam conceitos distintos.

**Arquivos e permissões:** o seletor de arquivos e a autorização de leitura/escrita são mecanismos de segurança do navegador e não podem ser substituídos ou ocultados pelo aplicativo. Nunca solicitar essas permissões automaticamente ou por temporizador; somente em uma ação explícita do usuário, como abrir, escolher ou autorizar o salvamento de um arquivo. Ao fechar a aba, não instalar uma confirmação nativa `beforeunload` — mostrar o estado do salvamento dentro do site.

**Salvamento automático:** após cada alteração, criar um backup local durável no navegador (por exemplo, IndexedDB) e sincronizar o JSON selecionado em intervalos de até dez segundos sempre que houver autorização de escrita. Guardar e restaurar o identificador do arquivo selecionado após recarregar o site, verificando a permissão sem abrir solicitações automáticas. Se a permissão não estiver disponível, preservar os dados no backup local, informar claramente que o JSON ainda não foi atualizado e permitir autorização mediante clique. Não sobrepor automaticamente um JSON modificado por outro programa; solicitar uma decisão dentro do aplicativo.

**Limites do backup:** os dados locais podem desaparecer quando o usuário limpa os dados do site, usa navegação privada ou muda de navegador/dispositivo. Por isso, manter a exportação JSON e avisar quando o backup falhar; não afirmar que um JSON foi atualizado enquanto o salvamento ocorreu apenas no navegador.

**Cartão de crédito:** data de compra, data de vencimento da fatura e data efetiva do pagamento são conceitos separados. Dia habitual de pagamento é referência opcional, não comprovação de pagamento. Mudanças cadastrais não reescrevem compras antigas nem pagamentos vinculados. Preservar o marco zero definido pelo saldo inicial.

Reutilizar este padrão em outros projetos e aplicativos desenvolvidos com a usuária.
