#!/bin/bash

cd ..
rm -rf __pycache__ /tmp/1.tar.gz
tar czvf /tmp/1.tar.gz --exclude='.git' --exclude='*.swp' furrynovels
