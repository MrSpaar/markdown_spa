#!/bin/bash
set -e

NC='\033[0m'
BOLD='\033[1m'
RED='\033[0;31m'
BLUE='\033[1;34m'
GREEN='\033[0;32m'

if ! command -v git &>/dev/null; then
    echo -e "${RED}${BOLD}Git not found. Please install git.${NC}"
    exit 1
fi

if command -v python &>/dev/null; then
    python=python
elif command -v python3 &>/dev/null; then
    python=python3
else
    echo -e "${RED}${BOLD}Python not found. Please install python 3.6 or higher.${NC}"
    exit 1
fi

if command -v pip &>/dev/null; then
    pip=pip
elif command -v pip3 &>/dev/null; then
    pip=pip3
elif command -v python -m pip &>/dev/null; then
    pip=python -m pip
else
    echo -e "${RED}${BOLD}Pip not found. Please install pip.${NC}"
    exit 1
fi

echo -ne "${BLUE}${BOLD}Enter where to setup the project (blank for current directory): ${NC}"
read -r

if [[ $REPLY != "" ]]; then
    mkdir -p $REPLY
    cd $REPLY
fi

git clone http://github.com/MrSpaar/Markdown-SPA.git .
rm -rf .git README.md setup.sh scss/main.scss pages/* && git init
find ./static -type f -not -name '*.js' -print0 | xargs -0 rm --

sed -i 's/scss\/main.scss//g' config.ini

echo -ne "${BLUE}${BOLD}Create a remote branch to your github repo? (Y/n)${NC} "
read -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo
    echo -ne "${BLUE}${BOLD}Enter the name of the remote branch: ${NC}"
    read -r

    git remote add origin $REPLY
fi

if ! $python -c 'import jinja2;import markdown;import pygments' &>/dev/null; then
    $pip install jinja2 markdown Pygments libsass
fi

if ! $python -c 'import livereload' &>/dev/null; then
    echo -ne "${BLUE}${BOLD}Install livereload (for easy testing)? (Y/n)${NC} "
    read -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $pip install livereload
    fi
fi

if ! $python -c 'import sass' &>/dev/null; then
    echo -ne "${BLUE}${BOLD}Install libsass (for SASS support)? (Y/n)${NC} "
    read -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $pip install sass
    fi
fi

echo -e "${GREEN}${BOLD}Dependencies installed.${NC}"
echo -e "${GREEN}${BOLD}Setup complete. Use ${BLUE}${BOLD}'python -m build'${GREEN}${BOLD} to build the site or ${BLUE}${BOLD}'python watch.py'${GREEN}${BOLD} to start a local server.${NC}"
