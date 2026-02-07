#!/usr/bin/env bash
set -e

sudo cp /home/d3/Documents/obsidian-vaults/master/global/homelab/services/scorify-client.service /etc/systemd/system
sudo cp /home/d3/Documents/obsidian-vaults/master/global/homelab/services/scorify-server.service /etc/systemd/system

sudo systemctl restart scorify-client
sudo systemctl restart scorify-server

