#! /usr/bin/env bash

rm -rf ./api/docs
cat ~/.ssh/github_repo_key.pub
git clone git@github.com:ideafast/ideafast-devicesupportdocs-web.git ./api/docs

# TODO: change to main branch once merged into master
cd ./api/docs
git checkout COS
cd