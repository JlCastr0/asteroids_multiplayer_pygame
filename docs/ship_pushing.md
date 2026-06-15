# Mecânica de Empurrão entre Naves (Ship Pushing)

Esta nova mecânica permite que as naves dos jogadores interajam fisicamente entre si, empurrando-se ao colidir, em vez de simplesmente atravessarem umas às outras.

## Funcionamento

Quando duas naves colidem, o motor de física resolve a colisão em duas etapas:

1.  **Resolução Estática**: As naves são afastadas imediatamente para que não fiquem sobrepostas.
2.  **Resolução Dinâmica**: Um impulso é aplicado a ambas as naves em direções opostas ao longo da normal da colisão. A força do impulso é definida pela constante `SHIP_PUSH_STRENGTH`.

### Detalhes Técnicos

A mecânica foi integrada à classe `CollisionManager` no arquivo `core/collisions.py`, seguindo a arquitetura original do jogo. Para suportar o mundo toroidal (wrapping), foram utilizadas funções utilitárias que calculam a distância e o delta mais curtos através das bordas do mapa.

-   **Determinismo**: Todo o cálculo de colisão ocorre no servidor (ou no loop principal do jogo), garantindo que todos os jogadores vejam o mesmo estado físico.
-   **Multiplayer**: Como as posições e velocidades das naves são sincronizadas via snapshots, o efeito de empurrão é propagado automaticamente para todos os clientes conectados. O sistema de predição do cliente suaviza eventuais correções de posição causadas pelo empurrão.

## Justificativa do Projeto

A implementação foi feita diretamente no `CollisionManager` para respeitar a separação de responsabilidades existente:
-   `Ship` lida com movimento básico e comandos.
-   `World` coordena as entidades.
-   `CollisionManager` resolve interações entre entidades.

Ao adicionar `_ship_vs_ships`, mantivemos a consistência com as outras mecânicas de colisão (como nave vs asteroide), utilizando as mesmas estruturas de dados e fluxo de execução. A inclusão de funções toroidais em `core/utils.py` melhorou a robustez não apenas desta mecânica, mas de todo o núcleo físico do jogo.

## Configuração

A força do empurrão pode ser ajustada em `core/config.py`:
-   `SHIP_PUSH_STRENGTH`: Define a velocidade mínima de separação aplicada no momento do impacto.
