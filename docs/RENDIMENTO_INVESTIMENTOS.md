# Rendimento, movimentações e gráficos

## Separar patrimônio de rendimento

O saldo mostra quanto existe no investimento. Aporte é dinheiro colocado; resgate é dinheiro retirado. Nenhum dos dois é, sozinho, rendimento ou prejuízo.

Entre duas avaliações, o resultado em reais é:

`saldo final - saldo anterior - aportes + resgates`.

Exemplo: R$ 1.000, aporte de R$ 200 e saldo final de R$ 1.200 representam resultado de R$ 0. Se o saldo final for R$ 1.250, o resultado é R$ 50. O mesmo vale para CDI, CDB, fundos e cripto: atualizar o patrimônio não substitui registrar o dinheiro que entrou ou saiu.

## Retorno estimado com as datas das movimentações

O percentual usa **Modified Dietz**:

`ganho = valor final - valor inicial - soma dos fluxos`

`capital médio = valor inicial + soma(fluxo × peso temporal)`

`retorno estimado = ganho / capital médio × 100`

Aportes são fluxos positivos; resgates são negativos. O peso é a fração do intervalo que resta após a movimentação. A convenção é de fim do dia: um fluxo na data final tem peso zero. Os dias são civis, calculados em UTC para não sofrer variações de fuso/horário de verão. O resultado não é anualizado nem é uma projeção contratual de CDI.

Exemplo sintético: R$ 1.000, resgate de R$ 900 e saldo final de R$ 105 em um intervalo de dez dias representam ganho de R$ 5. Se a retirada ocorrer após um dia, o capital médio é R$ 190 e o retorno estimado 2,63%; após nove dias, o capital médio é R$ 910 e a estimativa 0,55%. Dividir sempre pelos R$ 100 restantes produziria 5% nos dois casos e ignoraria o tempo do dinheiro.

Quando o investimento começa sem saldo, a janela de cálculo inicia no primeiro aporte, não em dias anteriores sem capital. Sem capital médio positivo, datas válidas ou duração suficiente para distinguir fluxos do mesmo dia, o percentual fica indisponível (—). Uma movimentação após a última avaliação não cria rendimento novo: é necessária outra avaliação.

O gráfico mensal considera o início do mês até cada avaliação registrada; o anual considera o início do ano. O valor inicial é o último saldo conhecido, transportado contabilmente. Se não houve avaliação no fechamento, essa base não é uma cotação exata de abertura; ganhos só observados na avaliação seguinte são reconhecidos nela. Não se inventa uma divisão de rendimento entre meses sem dados.

O quadro individual do mês atual mostra o **último intervalo entre avaliações**, calculado pelo mesmo estimador com as datas e os fluxos desse intervalo. Por representar outro intervalo, pode diferir do retorno estimado acumulado do mês. O resumo e o gráfico por tipo usam a mesma janela mensal/anual e consolidam valores e fluxos, em vez de calcular uma média das taxas dos investimentos. Avaliações faltantes ou antigas continuam sendo valores transportados, e a cobertura aparece no resumo; a consolidação também é estimativa.

Esse método corrige a hipótese anterior de que todos os fluxos teriam ocorrido no começo do intervalo. Não equivale a TWR exato com avaliações diárias. Para um TWR exato, seria necessário conhecer o valor de mercado nos pontos de movimentação. IRR/XIRR é outra métrica, ponderada pelo dinheiro e normalmente anualizada; não é apresentada silenciosamente como taxa mensal.

Valores brutos/líquidos, IR, IOF, taxas e spread precisam ser registrados em bases consistentes. O aplicativo não busca CDI diário nem adivinha impostos. O resultado reflete as avaliações e movimentações informadas.

Referências consultadas:

- [Portfolio Performance — Time-Weighted Rate of Return](https://github.com/portfolio-performance/portfolio-help/blob/master/docs/en/concepts/performance/time-weighted.md): necessidade de avaliações junto aos fluxos para retorno exato.
- [Portfolio Performance — Money-Weighted Rate of Return](https://github.com/portfolio-performance/portfolio-help/blob/master/docs/en/concepts/performance/money-weighted.md): importância das datas e diferença entre retorno do período e taxa anualizada.
- [OpenAlloc — Modified Dietz](https://github.com/openalloc/SwiftModifiedDietz): fórmula, capital médio e casos numéricos de referência usados na validação independente.

## Atualizar saldo, colocar dinheiro e resgatar

O fluxo comum tem três ações separadas. **Atualizar saldo** pede a data e o patrimônio atual (ou quantidade e cotação, em cripto), consulta o histórico automaticamente e mostra: última avaliação, aportes posteriores, resgates posteriores, saldo esperado sem rendimento, saldo atual informado e rendimento do intervalo. Não é necessário lembrar o saldo antes de uma retirada nem selecionar novamente uma movimentação já registrada.

**Colocar dinheiro** registra somente um aporte novo; **Resgatar** registra somente uma retirada nova. Valores do histórico são recompostos em centavos para evitar resíduos como 97,7400000000021 no formulário.

Quando uma atualização atravessa dois meses, o resultado observado corresponde ao intervalo inteiro desde a avaliação anterior. O mês anterior mantém o rendimento conhecido até sua última avaliação; o resultado ainda não observado é reconhecido na nova avaliação. Isso não constitui apuração exata do mês civil sem avaliação no fechamento.

Nos cartões do mês atual, o destaque é o rendimento desde a última avaliação, com datas do intervalo no título. Se não existir uma avaliação no mês selecionado, o cartão mostra Sem avaliação no período, mantém o último saldo registrado e não exibe rendimento, porcentagem nem minigráfico; aporte ou resgate sozinho não conta como avaliação. O resultado de um mês anterior continua acessível ao selecionar aquele mês. Os relatórios e gráficos mensais/anuais continuam disponíveis. O percentual desse intervalo usa o capital médio ponderado pelas datas dos fluxos e é identificado como estimado.

No Extrato, Investimento → Criptomoedas registra uma transferência geral: desconta o saldo da conta, aparece em azul e não altera nenhuma moeda. Criptomoedas individuais não são destinos de aportes pelo Extrato. O lançamento geral pode ser editado ou excluído sem alterar quantidade, cotação, patrimônio ou histórico das moedas.

Para criptomoedas, a ação é **Comprar cripto**: informar a data, o dinheiro desta compra, a quantidade total após a compra, a cotação atual, o total investido informado e, opcionalmente, o preço médio da corretora. O total investido é sugerido pelo cadastro anterior mais a nova compra e pode ser corrigido. O valor atual é calculado por quantidade total × cotação. A ação salva o aporte e a nova avaliação juntos, após validar todos os campos, sem exigir uma segunda atualização. O preço médio opcional ausente fica sem valor informado; ele não define o rendimento.

Depois de uma transferência geral, marcar **Este aporte já foi descontado no Extrato** em Comprar cripto. Isso registra o capital e a posição da moeda sem descontar novamente a conta. Para CDI/CDB, Colocar dinheiro continua sendo um aporte simples. O custo informado e o preço médio não são usados para inventar fluxos.

Aportes e resgates esquecidos ficam na ação separada **Corrigir histórico**, acessível pelo menu do investimento ou pelo próprio Histórico. Atualizar saldo não contém os campos de movimentação e ignora qualquer seleção antiga de correção. Recolher um painel não é usado como mecanismo para desligar uma operação financeira.

Aportes entram no Extrato como investimentos quando há saldo inicial de controle; resgates entram como entradas classificadas em Resgate, sem serem contados como receita. Metas vinculadas acompanham a valorização do capital reservado; o aporte novo ao investimento não aumenta a reserva existente.

## Corrigir a última atualização

Se uma movimentação foi esquecida na última atualização, marcar a opção de correção na janela Atualizar valor, selecionar aporte/resgate e informar o valor. O sistema insere o fluxo antes da avaliação já salva e preserva seu saldo final e sua data. A correção repetida é bloqueada. Atualizações antigas com eventos posteriores não são corrigidas automaticamente. Quando existem metas sem vínculo identificável com aquela avaliação, a correção é bloqueada para evitar alteração indevida das reservas.

Valores de exemplos e testes são fictícios. Não há migração automática de arquivos financeiros pessoais: o patrimônio final sozinho não revela quanto foi aporte nem quanto foi rendimento.

## Gráficos e verificação

Porcentagem é a visualização inicial. Valor (R$) continua disponível, com aviso de que aportes e resgates alteram a curva patrimonial. Mês e Ano selecionam o período; o gráfico anual em porcentagem mostra retorno acumulado no ano. Os minigráficos dos cartões também mostram a rentabilidade do período selecionado.

`node tests/invest-atualizacao-fluxos.test.js` cobre aporte, resgate, reinvestimento após retirada integral, cripto com compra adicional, correção de avaliação salva, reservas, datas e valores inválidos, preservação do estado em falhas, e gráficos mensal/anual em porcentagem e reais. `node tests/invest-retorno-fluxos.test.js` cobre o encadeamento de retornos e a ordem de eventos do mesmo dia. Ambos estão no fluxo de CI.

`node tests/rentabilidade-datas.test.js` verifica os pesos de datas, casos numéricos de referência, capital/datas inválidas, primeira aplicação, consolidação sem média de taxas e preservação do histórico.
