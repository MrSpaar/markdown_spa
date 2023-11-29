read -p "Create a new directory? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    read -p "Enter the name of the directory: " -r
    mkdir $REPLY
    cd $REPLY
fi

git clone http://github.com/MrSpaar/Markdown-SPA.git .
rm -rf .git README.md setup.sh
git init

read -p "Enter your repository URL: " -r
git remote add origin $REPLY
git add .

python -m pip install markdown jinja2 pygments libsass

read -p "Do you want to install 'watchdog' to automatically rebuild the site when a file changes? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python -m pip install watchdog
fi

echo "Setup complete. Use 'python -m build' to build the site or 'python watch.py' to start a local server."