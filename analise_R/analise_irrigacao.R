# Carregar as bibliotecas necessárias
library(readr)
library(rpart)
library(rpart.plot)

# --- 1. CARREGAR OS DADOS (DE FORMA MAIS ROBUSTA) ---

# <<< ALTERAÇÃO AQUI >>>
# Especificamos o tipo de cada coluna para evitar que o R interprete errado.
# t = timestamp (character), d = double (número com decimal), i = integer (inteiro), f = factor (categórico)
tipos_colunas <- cols(
  timestamp = col_character(),
  n = col_integer(),
  p = col_integer(),
  k = col_integer(),
  ph = col_double(),
  umidade = col_double(),
  acao_bomba = col_factor()
)

# Ler o arquivo CSV usando os tipos de coluna que definimos.
# Lembre-se de ajustar o caminho se necessário.
dados_irrigacao <- read_csv("sensores-Trab1_fase2_cap1/historico_irrigacao.csv", col_types = tipos_colunas)


# --- O RESTO DO CÓDIGO CONTINUA O MESMO ---

# Visualizar as primeiras linhas para confirmar que os tipos estão corretos agora
print(head(dados_irrigacao))
print(summary(dados_irrigacao))

# Construir o modelo de árvore de decisão
modelo_arvore <- rpart(
  acao_bomba ~ umidade + ph + n + p + k,
  data = dados_irrigacao,
  method = "class"
)

# Plotar a nova árvore de decisão
rpart.plot(
  modelo_arvore,
  main = "Árvore de Decisão para Irrigação da FarmTech (v2)",
  box.palette = "Blues",
  shadow.col = "gray",
  nn = TRUE
)

# Imprimir um resumo das regras
printcp(modelo_arvore)