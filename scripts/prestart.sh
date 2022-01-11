#! /usr/bin/env bash

mkdir -p ~/.ssh
cp ../tmp/github_repo_key ~/.ssh/github_repo_key
cp ../tmp/github_repo_key.pub ~/.ssh/github_repo_key.pub

# change permissions on file
chmod 600 ~/.ssh/github_repo_key
chmod 600 ~/.ssh/github_repo_key.pub

# start the ssh-agent in the background
eval $(ssh-agent -s)

# make ssh agent to actually use copied key
ssh-add ~/.ssh/github_repo_key

# ad github as a known host
ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts

# clone the repo for the first time
. ./pull_repo.sh
