# Trabalho 1 - SCC0250 (Computação Gráfica)

**Docente:** Prof. Ricardo Marcacini

**Aluno PAE:** João Lucas Sarcinelli

| Alunos  | NUSP |
|-------|----|
| Adalton de Sena Almeida Filho  | 12542435 |
| Rafael Zimmer | 12542612 |

## Objetivo

Construir um cenário 3D a partir de modelos/malhas pré-existentes e com aplicação de 
textura. O programa deve permitir explorar o cenário por meio de manipulação da câmera
(Matrizes Model x View x Projection).

## Requisitos

1. O cenário deve conter um ambiente interno e externo.
2. O ambiente interno pode ser obtido por meio de uma habitação, como casa, prédio,
 cabana, entre outros.
3. Adicione pelo menos três modelos dentro da habitação (ambiente interno). Por
 exemplo, se o ambiente interno for uma casa, então a casa pode conter móveis
 como sofá e televisão. Também pode conter moradores, como humanos e animais
 de estimação.
4. O terreno/chão da habitação deve ter alguma textura diferente do ambiente externo.
5. O terreno/chão do ambiente externo deve ter no mínimo duas texturas diferentes.
 Por exemplo, uma parte do terreno pode ser grama e outra parte asfalto/pedra.
6. O ambiente externo deve ter no mínimo três modelos, como árvores, carros,
 pessoas, animais, entre outros.
7. Escolha pelo menos 1 modelo para aplicar transformações geométricas de rotação,
 escala e translação, conforme eventos do teclado.
8. O seu cenário deve ter um céu para o ambiente externo, com sua respectiva textura.
 Dica: pesquisar SkyBox.
9. O seu programa deve restringir a exploração do cenário dentro dos limites da
 “borda” do céu e terreno. Não é necessário restringir o acesso aos modelos, ou seja,
 a câmera pode passar livremente “por dentro” dos modelos (com exceção do céu e
 terreno).
10. O seu programa deve permitir ativar o modo de visualização de malha poligonal a
 qualquer momento, pressionando a tecla P. Ao pressionar novamente a tecla P,
 voltar ao modo textura.

## Entrega

[Link do vídeo]()

[GitHub](https://github.com/rzimmerdev/cg)

## Execução

Para rodar, use:
```
python main.py
```

Para instalar dependencias:

```
pip install -r requirements.txt
```


Para criar ambiente virtual com Anaconda ou Miniconda:

```
conda env create -f environment.yml
```

```bash
gsettings set org.gnome.mutter check-alive-timeout 60000
```
