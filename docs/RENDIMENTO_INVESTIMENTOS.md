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

## Atualizar valor

No Extrato, Investimento → Criptomoedas registra uma transferência geral: desconta o saldo da conta, aparece em azul e não altera nenhuma moeda. Criptomoedas individuais não são destinos de aportes pelo Extrato. O lançamento geral pode ser editado ou excluído sem alterar quantidade, cotação, patrimônio ou histórico das moedas.

Ao atualizar uma moeda depois de uma transferência geral, informar o aporte e marcar **Este aporte já foi descontado no Extrato**. Isso registra o fluxo no histórico da moeda para separar capital de rendimento, sem gerar um segundo desconto na conta. O lançamento geral continua sem vínculo com uma moeda específica. A opção também vale para corrigir um aporte esquecido na última atualização.

- Informar o patrimônio final, já com as compras ou retiradas. Em cripto, ele é quantidade × cotação, arredondado para centavos.
- Selecionar o aporte ou resgate ainda não registrado e informar somente o dinheiro novo movimentado, na data do campo de atualização.
- Se o fluxo já consta no Extrato ou no histórico, selecionar Nenhuma. Não registrá-lo novamente.
- Informar, se disponível, o patrimônio imediatamente antes da movimentação para melhorar a rentabilidade.
- O campo Valor investido da cripto é informativo e não cria, sozinho, aporte ou lançamento no Extrato. Não é seguro inferir fluxos apenas pela variação do custo acumulado ou da quantidade.

Aportes entram no Extrato como investimentos quando há saldo inicial de controle; resgates entram como entradas classificadas em Resgate, sem serem contados como receita. Metas vinculadas acompanham a valorização do capital reservado; o aporte novo ao investimento não aumenta a reserva existente.

## Corrigir a última atualização

Se uma movimentação foi esquecida na última atualização, marcar a opção de correção na janela Atualizar valor, selecionar aporte/resgate e informar o valor. O sistema insere o fluxo antes da avaliação já salva e preserva seu saldo final e sua data. A correção repetida é bloqueada. Atualizações antigas com eventos posteriores não são corrigidas automaticamente. Quando existem metas sem vínculo identificável com aquela avaliação, a correção é bloqueada para evitar alteração indevida das reservas.

Valores de exemplos e testes são fictícios. Não há migração automática de arquivos financeiros pessoais: o patrimônio final sozinho não revela quanto foi aporte nem quanto foi rendimento.

## Gráficos e verificação

Porcentagem é a visualização inicial. Valor (R$) continua disponível, com aviso de que aportes e resgates alteram a curva patrimonial. Mês e Ano selecionam o período; o gráfico anual em porcentagem mostra retorno acumulado no ano. Os minigráficos dos cartões também mostram a rentabilidade do período selecionado.

`node tests/invest-atualizacao-fluxos.test.js` cobre aporte, resgate, reinvestimento após retirada integral, cripto com compra adicional, correção de avaliação salva, reservas, datas e valores inválidos, preservação do estado em falhas, e gráficos mensal/anual em porcentagem e reais. `node tests/invest-retorno-fluxos.test.js` cobre o encadeamento de retornos e a ordem de eventos do mesmo dia. Ambos estão no fluxo de CI.
