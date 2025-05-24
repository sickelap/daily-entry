#!/usr/bin/env bash

PYTEST_COV_FLAGS="--cov --cov-report=html --cov-report=term --cov-fail-under=90"

if [[ $1 == "watch" ]]; then
  ptw -- $PYTEST_COV_FLAGS
else
  pytest $PYTEST_COV_FLAGS
fi
