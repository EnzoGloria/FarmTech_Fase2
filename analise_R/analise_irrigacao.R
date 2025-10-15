library(readr)
library(rpart)
library(rpart.plot)

tipos_colunas <- cols(
  timestamp = col_character(),
  n = col_integer(),
  p = col_integer(),
  k = col_integer(),
  ph = col_double(),
  umidade = col_double(),
  acao_bomba = col_factor()
)

dados_irrigacao <- read_csv("sensores-Trab1_fase2_cap1/historico_irrigacao.csv", col_types = tipos_colunas)


print(head(dados_irrigacao))
print(summary(dados_irrigacao))

modelo_arvore <- rpart(
  acao_bomba ~ umidade + ph + n + p + k,
  data = dados_irrigacao,
  method = "class"
)

rpart.plot(
  modelo_arvore,
  main = "Árvore de Decisão para Irrigação da FarmTech (v2)",
  box.palette = "Blues",
  shadow.col = "gray",
  nn = TRUE
)

printcp(modelo_arvore)
