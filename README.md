# Caminhos de Lume

Protótipo jogável de exploração em tiles com Python, Pygame e pytmx. Inclui três áreas conectadas, câmera, colisões, quatro NPCs, diálogos, sete baús, mochila, mapa da área, missão com final e salvamento.

## Jogar no seu computador

instale Python 3.10 ou mais recente. 

```sh
python -m pip install -r requirements.txt
python game.py
```

No Windows, `Jogar.bat` inicia o jogo após instalar as dependências. É necessário ambiente gráfico. 

## Controles e missão

| Ação | Tecla |
|---|---|
| Andar | WASD ou setas |
| Conversar, abrir baú, ler placa, ativar farol | E ou Enter |
| Avançar diálogo | E, Enter ou espaço |
| Mapa da área | M |
| Mochila | I ou Tab |
| Ajuda | F1 |
| Salvar / carregar | F5 / F9 |
| Fechar painel/diálogo; fora deles, salvar e sair | Esc |

Fale com Iara na praça. Encontre um fragmento em cada área e leve os três ao farol ao norte da vila. O baú no noroeste do bosque contém a chave das ruínas. Caminhe sobre uma passagem para mudar de mapa. A passagem aparece como um círculo dourado com uma seta.

Você pode explorar livremente, visitar áreas anteriores e obter os tesouros antes de falar com Iara. A chave só é necessária para entrar nas ruínas. Baús abertos e a recompensa final não podem ser coletados novamente.

Este protótipo tem foco em exploração e diálogos, sem combate. A moeda funciona como tesouro acumulado; não há loja nesta aventura. O jogo não tem trilha sonora; o vídeo de demonstração acrescenta voz e música sintetizada.

## Salvar

Localização, baús, moedas, chave, fragmentos e missão ficam em `saves/save.json`. Há salvamento automático ao atravessar mapas, abrir baús, obter a missão, concluir o objetivo e sair. Use F5 para salvar a localização a qualquer momento. Para recomeçar, mova esse arquivo para um backup antes de abrir o jogo.

## Mapas editáveis no Tiled

Os arquivos **TMX/TSX são carregados de verdade pelo pytmx**. Foram gerados por `build_maps.py`, não desenhados manualmente na interface do editor, e estão prontos para abrir e editar no Tiled:

- `assets/vila.tmx`: Vila de Lume (32 × 24 tiles).
- `assets/bosque.tmx`: Bosque das Lanternas (48 × 30 tiles).
- `assets/ruinas.tmx`: Ruínas da Primeira Luz (32 × 24 tiles).
- `assets/lume.tsx`: tileset externo de 32 × 32 pixels.
- `assets/tiles.png`: arte original do tileset.

Abra um TMX no Tiled, edite e salve. Reinicie o jogo para carregar a alteração. Preserve os caminhos relativos entre o TMX, o TSX e o PNG. `build_maps.py` regenera e substitui os mapas; não o execute sobre edições que queira preservar.

Camadas: `Chao`, `Detalhes` e `Objetos`. A propriedade booleana `solid` dos tiles controla a colisão. Objetos interativos ocupam uma célula e usam coordenadas alinhadas a 32 pixels; largura e altura devem continuar em 32.

| Tipo do objeto | Propriedades |
|---|---|
| `npc` | `dialog` para os personagens da missão; `text` opcional, com páginas separadas por `\|`, para diálogo personalizado |
| `chest` | nome único; `reward`: `gold`, `fragment` ou `key`; `amount` |
| `sign` | `text` |
| `portal` | `destination`: `vila`, `bosque` ou `ruinas`; `spawn_x`/`spawn_y` em tiles; `requires=key` opcional |
| `beacon` | ponto de conclusão da missão |

Mantenha os nomes únicos dos baús para que os saves continuem válidos. Pontos de entrada devem ser transitáveis e não sobre outro portal. Os diálogos de missão e a quantidade de três fragmentos estão em `world.py`; novos mapas precisam ser registrados em `MAPS`.

## Verificação e gravação

```sh
python -m unittest -v test_world
python game.py --smoke
python demo.py
```

Os testes verificam a missão completa, acesso a todos os objetos, chave/portão, colisões, recompensas únicas e persistência. A gravação usa as ações reais do jogo, com deslocamentos acelerados e progresso separado do save do jogador.

`build_maps.py` requer Pillow apenas para regenerar a arte e os mapas; os assets já estão incluídos e jogar não precisa de Pillow.
