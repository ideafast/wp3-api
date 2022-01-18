#! /usr/bin/env bash

# start the ssh-agent in the background
eval $(ssh-agent -s)

# make ssh agent to actually use copied key
ssh-add ~/.ssh/id_ed25519

# ad github as a known host
ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts

# clone the repo for the first time
rm -rf ./api/docs
git clone git@github.com:ideafast/ideafast-devicesupportdocs-web.git ./api/docs
