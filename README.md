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

## Requisitos I

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

## Requisitos II

1. Um dos objetos externos deve ter animação, com alguma translação envolvida. 
Caso o Trabalho 1 já contenha tal objeto, então ele pode ser reutilizado. 
Esse objeto com animação será uma fonte de luz.
2. Um objeto interno (a uma casa ou modelo similar) representará uma fonte de luz estática.
3. A fonte de luz do ambiente interno só deve afetar os objetos dentro do ambiente interno.
4. A fonte de luz do ambiente externo só deve afetar os objetos do ambiente externo.
5. Determine alguns eventos de teclado para incrementar ou decretar a luz ambiente.
6. Determine alguns eventos de teclado para aumentar a reflexão difusa das fontes de luz.
7. Determine alguns eventos de teclado para aumentar a reflexão especular das fontes de luz.
8. Todo objeto do seu cenário deve ter seus próprios parâmetros de iluminação difusa e especular.
9. Bônus: sua fonte de luz pode aumentar ou reduzir a iluminação conforme a distância da fonte de luz em relação aos objetos.

## Entrega I

[Link do vídeo](https://youtu.be/Il1wCbGvCUo)

![Thumbnail](thumbnail1.png)

## Entrega II

https://www.youtube.com/watch?v=L6tP9GwjHJs

![Thumbnail](thumbnail2.png)

[GitHub](https://github.com/rzimmerdev/cg)

## Execução

Para evitar que a janela congele:

```bash
gsettings set org.gnome.mutter check-alive-timeout 60000
```

Caso não tenha instalado o LFS do Git instalado, e tenha clonado o projeto, ou baixe o projeto com os arquivos descompactados, ou instale o [LFS](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage)

Para criar ambiente virtual com Anaconda ou Miniconda:

```
conda env create -f environment.yml
```

Para instalar as dependencias:

```
pip install -r requirements.txt
```

Para rodar, use (Importante: Veja a seção de controles para saber como controlar o jogo):
Inicicialmente, o jogo tem o Mouse em modo "detached", 
para ativar o modo "attached" entre em Tela Cheia (F11).
```
python main.py
```


## Módulos principais:

### Components

Contém: `Model`, `Object`, `Player`, `Scene`.

A classe `Model` é responsável por carregar e renderizar um modelo 3D.
Ela também envia para a GPU as informações necessárias para renderizar o modelo.

A classe `Object` é responsável por representar uma visualização de um modelo 3D no espaço.
Ela contém uma referência para um `Model`, calcula uma matriz de transformação com base em alguns atributos:
- `position`: posição do objeto no espaço
- `rotation`: rotação do objeto no espaço
- `scale`: escala do objeto no espaço

A classe `Player` é apenas um `Object` com algumas funcionalidades adicionais, como movimentação e rotação.
Essa classe tem uma função de tick que lê do teclado e atualiza a posição e rotação do objeto.

A classe `Scene` é apenas um container para objetos. Ela é responsável por renderizar todos os objetos que ela contém.
Suas funções de manipulação de objetos alteram a raiz do objeto no mundo, 
sendo possível adicionar objetos em relação a outros objetos por exemplo.

Além disso, dentro do módulo de `Object`, temos a classe `Light`, que é responsável por representar uma fonte de luz.

### Engine

Contém: `Engine`.

A classe `Engine` é responsável por gerenciar todos objetos e cenários existentes.


### View

Contém: `Camera`, `Window`, `Shader`

A classe `Camera` é um dataclass que contém informações sobre a câmera, como posição, direção e up.

A classe `Window` é responsável por criar uma janela e gerenciar a renderização.
Ela guarda informações básicas sobre a janela, como posição e tamanho, e faz as chamadas para o glfw.

A classe `Shader` é responsável por compilar e linkar shaders. Lê os arquivos GSLS e compila para a GPU.


### Game

É a classe principal. Contém o game loop, e é responsável por instanciar um programa de Shader, uma Engine e um Window.
No momento contém apenas uma camera, e a função de movimentar a câmera.


## Controles

Jogo:
- P: Alternar entre visualização de textura e malha poligonal
- F11: Alternar entre fullscreen e janela
- ESC: Sair do programa


Jogador + Camera:
- W, A, S, D: Movimentar a câmera
- Mouse: Rotacionar a câmera
- Shift, Espaço: Subir e descer a câmera


Fabienne:
- Setas: Movimentar o objeto
- Right Ctrl, Right Shift: Rotacionar o objeto no eixo Y
- Right Bracket, Left Bracket: Rotacionar o objeto no eixo X
- \- e +: Escalar o monstro
- 1 e 2: Altera o coeficiente de reflexão difusa
- 3 e 4: Altera o coeficiente de reflexão especular
- 5 e 6: Altera o expoente de reflexão especular
- 0 e 9: Altera o coeficiente de reflexão ambiente

Luzes:
- C e V: Altera a intensidade da luz ambiente externa
- F e G: Animam o objeto de luz externo (ovni)
- H e J: Alteram a intensidade da fonte de luz externa
