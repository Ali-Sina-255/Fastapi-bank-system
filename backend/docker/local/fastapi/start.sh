#!/bin/bash

set -o  errexit

set -o nounset

set -o pipefail

exec unicorn backend.app.main:app --host 0.0.0.0 8000 --reload
