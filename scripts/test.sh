#!/usr/bin/env bash

PYTEST_COV_FLAGS="--cov --cov-report=html --cov-report=term --cov-fail-under=90"

if [[ $1 == "singlerun" ]]; then
  pytest $PYTEST_COV_FLAGS
else
  ptw -- $PYTEST_COV_FLAGS
fi
