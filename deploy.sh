echo "Switching to branch master"
git checkout master

echo "Building app..."
npm run build

echo "Deploying files to server..."
scp -r build/* viktor@DESKTOP-THDUD6S:/var/www/111/