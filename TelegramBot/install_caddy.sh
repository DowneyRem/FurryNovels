#!/bin/bash
cd /tmp
wget --no-check-certificate https://github.com/caddyserver/caddy/releases/download/v2.6.2/caddy_2.6.2_linux_amd64.deb
dpkg -i caddy_2.6.2_linux_amd64.deb
rm -v caddy_2.6.2_linux_amd64.deb
