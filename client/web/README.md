# Astergard Web Client

Frontend shell D59.4 dla klienta webowego Astergardu.

## Wymagania

- Node.js 20+.
- `npm`.
- Działający backend Astergardu z WebSocket gatewayem `astergard.v1`.

## Instalacja

```bash
npm ci
```

## Konfiguracja

Ustaw `VITE_ASTERGARD_WS_URL` na adres gatewaya WebSocket.

- przykład lokalny: `ws://127.0.0.1:4001`
- produkcja: wymagane `wss://...`

Jeśli zmienna nie jest ustawiona, tryb developerski używa `ws://127.0.0.1:4001`.

## Uruchomienie

1. Uruchom backend Astergardu.
2. Upewnij się, że origin lokalnego Vite jest dopuszczony w allowliście backendu.
3. Uruchom frontend:

```bash
npm run dev
```

## Testy

```bash
npm run lint
npm run typecheck
npm test
```

## Build

```bash
npm run build
```

## Ograniczenia D59.4

- brak mapy graficznej;
- brak paneli postaci, walki i ekwipunku;
- brak tworzenia nowej postaci;
- brak reconnect token;
- brak pluginów, aliasów, triggerów i automatyzacji;
- brak Monaco;
- brak PWA i service workera.

## Bezpieczeństwo

- Hasło nie jest zapisywane w `localStorage`, `sessionStorage`, URL ani logach aplikacji.
- Terminal renderuje ANSI bez `dangerouslySetInnerHTML`.
- Produkcja wymaga `WSS`.
