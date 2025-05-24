#!/usr/bin/env bash

if [[ $1 == "watch" ]]; then
  ptw
else
  pytest
fi
