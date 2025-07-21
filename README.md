# Solana Arbitrage Bot MVP

Автономный арбитражный бот для Solana с использованием Flash Loan (MarginFi) и атомарных сделок на DEX (Orca, Raydium, Phoenix, Jupiter).

## Структура проекта

- `offchain/` — Python-бот для мониторинга и отправки транзакций
- `onchain/` — Anchor-программа для Flash Loan и swap-ов
- `requirements.txt` — зависимости Python-бота
- `Anchor.toml` — конфиг Anchor-программы

## MVP функционал
- Мониторинг цен на DEX
- Поиск арбитражных возможностей
- Получение Flash Loan (MarginFi)
- Атомарные swap-ы на DEX
- Возврат Flash Loan
