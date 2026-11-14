# ai_companion

Рабочая кодовая база для AI-среды Artur’а.

## AI Computer (Instagram Reels)

Каталог [`ai_computer/`](ai_computer/) — стек удалённого Ubuntu-компьютера для агента:

- XFCE + xrdp (доступ через SSH-туннель)
- Google Chrome с постоянным профилем
- Playwright → CDP только на `127.0.0.1`
- Codex CLI через вход ChatGPT Go (без API-биллинга по умолчанию)
- Публикация Reels только после явного `reels confirm`

См. [ai_computer/README.md](ai_computer/README.md) и [ai_computer/docs/setup.md](ai_computer/docs/setup.md).
