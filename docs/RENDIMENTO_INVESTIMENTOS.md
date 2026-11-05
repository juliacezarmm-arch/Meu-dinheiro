# Rendimento, movimentações e gráficos

## Separar patrimônio de rendimento

O saldo mostra quanto existe no investimento. Aporte é dinheiro colocado; resgate é dinheiro retirado. Nenhum dos dois é, sozinho, rendimento ou prejuízo.

Entre duas avaliações, o resultado em reais é:

`saldo final - saldo anterior - aportes + resgates`.

Exemplo: R$ 1.000, aporte de R$ 200 e saldo final de R$ 1.200 representam resultado de R$ 0. Se o saldo final for R$ 1.250, o resultado é R$ 50. O mesmo vale para CDI, CDB, fundos e cripto: atualizar o patrimônio não substitui registrar o dinheiro que entrou ou saiu.

## Porcentagem por avaliações

O aplicativo encadeia fatores de retorno entre avaliações (abordagem TWR): `produto(1 + retorno de cada intervalo) - 1`. Aporte e resgate preservam o fator acumulado; não criam picos na curva percentual. Os eventos do mesmo dia seguem a ordem de registro, inclusive aporte, atualização e resgate.

Quando se informa o saldo imediatamente antes da movimentação, a atualização registra essa avaliação, depois o aporte/resgate, depois o saldo final. Exemplo: R$ 1.000 passam a R$ 1.100; um aporte de R$ 200 leva a R$ 1.300. O rendimento é R$ 100 e a rentabilidade é 10%, não 30%.

Sem uma avaliação junto à movimentação não é possível reconstruir um TWR exato. O aplicativo usa o último saldo conhecido e trata o fluxo como anterior à avaliação seguinte. A interface identifica essa limitação: o resultado percentual é aproximado. Não se utiliza média de CDI, cotação externa ou preço médio de compra para inventar avaliações ausentes. A taxa mensal não é anualizada; a curva anual encadeia as avaliações desde o início do ano.

Os valores informados determinam se o patrimônio é bruto ou líquido. O aplicativo não estima automaticamente IR, IOF, taxas ou spread. Para acompanhar o líquido, utilizar avaliações líquidas de forma consistente. Taxas descontadas do investimento e não registradas separadamente permanecem no resultado observado.

O percentual geral de vários investimentos continua sendo uma aproximação ponderada pelo capital de referência, não um TWR exato de carteira consolidada.

## Atualizar saldo, colocar dinheiro e resgatar

O fluxo comum tem três ações separadas. **Atualizar saldo** pede a data e o patrimônio atual (ou quantidade e cotação, em cripto), consulta o histórico automaticamente e mostra: última avaliação, aportes posteriores, resgates posteriores, saldo esperado sem rendimento, saldo atual informado e rendimento do intervalo. Não é necessário lembrar o saldo antes de uma retirada nem selecionar novamente uma movimentação já registrada.

**Colocar dinheiro** registra somente um aporte novo; **Resgatar** registra somente uma retirada nova. Valores do histórico são recompostos em centavos para evitar resíduos como 97,7400000000021 no formulário.

Exemplo de intervalo atravessando meses: avaliação de R$ 3.307,78 em 28/10, resgate de R$ 350,01 em 30/10 e resgates de R$ 2.820,01 e R$ 40,02 em novembro deixam saldo conhecido de R$ 97,74. Uma nova avaliação de R$ 102,49 em 04/11 reconhece R$ 4,75 de rendimento, sem lançar novamente as retiradas. O mês anterior mantém o rendimento conhecido até sua última avaliação; o resultado ainda não observado é reconhecido na nova avaliação. Não se inventa uma divisão entre dias ou meses sem dados do banco.

Nos cartões do mês atual, o destaque é o rendimento desde a última avaliação, com datas do intervalo no título. Se não existir uma avaliação no mês selecionado, o cartão mostra Sem avaliação no período, mantém o último saldo registrado e não exibe rendimento, porcentagem nem minigráfico; aporte ou resgate sozinho não conta como avaliação. O resultado de um mês anterior continua acessível ao selecionar aquele mês. Os relatórios e gráficos mensais/anuais continuam disponíveis. O percentual desse intervalo usa o saldo esperado após os fluxos e é aproximado quando não houve avaliações nas datas das movimentações.

No Extrato, Investimento → Criptomoedas registra uma transferência geral: desconta o saldo da conta, aparece em azul e não altera nenhuma moeda. Criptomoedas individuais não são destinos de aportes pelo Extrato. O lançamento geral pode ser editado ou excluído sem alterar quantidade, cotação, patrimônio ou histórico das moedas.

Depois de uma transferência geral, usar **Colocar dinheiro** na moeda e marcar **Este aporte já foi descontado no Extrato**. Em seguida atualizar quantidade/cotação em **Atualizar saldo**. Isso registra o capital no histórico da moeda sem descontar novamente a conta. O custo informado e o preço médio não são usados para inventar fluxos.

Aportes e resgates esquecidos ficam na ação separada **Corrigir histórico**, acessível pelo menu do investimento ou pelo próprio Histórico. Atualizar saldo não contém os campos de movimentação e ignora qualquer seleção antiga de correção. Recolher um painel não é usado como mecanismo para desligar uma operação financeira.

Aportes entram no Extrato como investimentos quando há saldo inicial de controle; resgates entram como entradas classificadas em Resgate, sem serem contados como receita. Metas vinculadas acompanham a valorização do capital reservado; o aporte novo ao investimento não aumenta a reserva existente.

## Corrigir a última atualização

Se uma movimentação foi esquecida na última atualização, marcar a opção de correção na janela Atualizar valor, selecionar aporte/resgate e informar o valor. O sistema insere o fluxo antes da avaliação já salva e preserva seu saldo final e sua data. A correção repetida é bloqueada. Atualizações antigas com eventos posteriores não são corrigidas automaticamente. Quando existem metas sem vínculo identificável com aquela avaliação, a correção é bloqueada para evitar alteração indevida das reservas.

Valores de exemplos e testes são fictícios. Não há migração automática de arquivos financeiros pessoais: o patrimônio final sozinho não revela quanto foi aporte nem quanto foi rendimento.

## Gráficos e verificação

Porcentagem é a visualização inicial. Valor (R$) continua disponível, com aviso de que aportes e resgates alteram a curva patrimonial. Mês e Ano selecionam o período; o gráfico anual em porcentagem mostra retorno acumulado no ano. Os minigráficos dos cartões também mostram a rentabilidade do período selecionado.

`node tests/invest-atualizacao-fluxos.test.js` cobre aporte, resgate, reinvestimento após retirada integral, cripto com compra adicional, correção de avaliação salva, reservas, datas e valores inválidos, preservação do estado em falhas, e gráficos mensal/anual em porcentagem e reais. `node tests/invest-retorno-fluxos.test.js` cobre o encadeamento de retornos e a ordem de eventos do mesmo dia. Ambos estão no fluxo de CI.
