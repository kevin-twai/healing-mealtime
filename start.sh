#!/bin/bash
exec gunicorn -w 2 -t 120 -b 0.0.0.0:10000 app:app