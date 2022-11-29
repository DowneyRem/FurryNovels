#!/bin/bash

systemctl --user stop furrynovels
cp ./furrynovels.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user start furrynovels
