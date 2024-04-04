#!/bin/bash
python3 src/document_reader.py &
python3 serve_react.py &
open http://localhost:8000
