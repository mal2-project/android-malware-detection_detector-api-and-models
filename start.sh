#!/bin/sh


uvicorn --reload --host 0.0.0.0 --port 8000 app.main:app
