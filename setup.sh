LIGHT_BLUE='\033[1;34m'
GREEN='\033[0;32m'
NC='\033[0m'
BOLD='\033[1m'

echo -ne "${LIGHT_BLUE}${BOLD}Create a new directory? (Y/n)${NC} "
read -n 1 -r

echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo -ne "${LIGHT_BLUE}${BOLD}Enter the name of the directory: ${NC}"
    read -r

    mkdir $REPLY
    cd $REPLY
fi

git clone http://github.com/MrSpaar/Markdown-SPA.git .
rm -rf .git README.md setup.sh
git init

echo -ne "${LIGHT_BLUE}${BOLD}Create a remote branch to your github repo? (Y/n)${NC} "
read -n 1 -r

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo
    echo -ne "${LIGHT_BLUE}${BOLD}Enter the name of the remote branch: ${NC}"
    read -r

    git remote add origin $REPLY
fi


python -m pip install markdown jinja2 pygments libsass

echo -ne "${LIGHT_BLUE}${BOLD}Install watchdog (test server + file watcher)? (Y/n)${NC} "
read -n 1 -r

echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python -m pip install watchdog
fi

echo -e "${GREEN}${BOLD}Setup complete. Use 'python -m build' to build the site or 'python watch.py' to start a local server.${NC}"