LIGHT_BLUE='\033[1;34m'
GREEN='\033[0;32m'
NC='\033[0m'
BOLD='\033[1m'

echo -ne "${LIGHT_BLUE}${BOLD}Enter where to setup the project (blank for current directory): ${NC}"
read -r

if [[ $REPLY != "" ]]
then
    mkdir -p $REPLY
    cd $REPLY
fi

git clone http://github.com/MrSpaar/Markdown-SPA.git .
rm -rf .git README.md setup.sh pages/* static/*.jpg static/*.png
echo "name: Main Page

# Hello World!" > pages/index.md
git init

echo -ne "${LIGHT_BLUE}${BOLD}Create a remote branch to your github repo? (Y/n)${NC} "
read -n 1 -r
echo

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

echo -e "${GREEN}${BOLD}Setup complete. Use ${LIGHT_BLUE}${BOLD}'python -m build'${GREEN}${BOLD} to build the site or ${LIGHT_BLUE}${BOLD}'python watch.py'${GREEN}${BOLD} to start a local server.${NC}"