#!/bin/bash
# linkup-docs 최초 push 스크립트
# GitHub Organization 이름을 아래에 입력하세요

GITHUB_ORG="YOUR_ORG_OR_USERNAME"   # ← 수정 필요
REPO_NAME="linkup-docs"

git remote add origin "https://github.com/${GITHUB_ORG}/${REPO_NAME}.git"
git push -u origin main
