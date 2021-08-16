#!/bin/sh
cd frontend && npm install && npm run build && cd ..
mkdir -p exhibition/www && cp -r frontend/build/* exhibition/www
