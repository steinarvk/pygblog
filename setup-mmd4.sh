#!/bin/bash
git clone https://github.com/fletcher/MultiMarkdown-4.git
pushd MultiMarkdown-4
git submodule init
git submodule update
make
popd
