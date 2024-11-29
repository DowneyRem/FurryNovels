#!/bin/bash
python TelegramBot.py &
caddy reverse-proxy --from :8880 --to :8080
