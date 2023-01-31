#!/bin/sh
cd ../app
celery -A parser.main worker -l INFO
