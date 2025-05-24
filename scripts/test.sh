#!/usr/bin/env bash

if [[ $1 == "watch" ]]; then
  ptw -- --cov --cov-report=html --cov-report=term
else
  pytest --cov --cov-report=html --cov-report=term
fi
