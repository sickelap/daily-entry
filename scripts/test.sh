#!/usr/bin/env bash

if [[ $1 == "watch" ]]; then
  ptw -- --cov
else
  pytest --cov
fi
