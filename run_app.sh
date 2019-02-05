#!/bin/bash
pkill node
pkill npm
pkill -9 python
cd Python
python3 main.py &
cd ../React
npm start &
