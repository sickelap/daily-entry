#!/usr/bin/env bash

PYTEST_COV_FLAGS="--cov --cov-report=html --cov-report=term --cov-fail-under=90"

if [[ $1 == "watch" ]]; then
  ptw -- --cov --cov-report=html --cov-report=term
else
  pytest --cov --cov-report=html --cov-report=term
fi
