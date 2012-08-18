templates:
	echo "module.exports = " > pecan.js/templates.js
	node build_templates.js >> pecan.js/templates.js

build:
	npm install
	make templates    
	node_modules/.bin/browserify -r br-jquery -r plate pecan.js/site.js > src/media/js/bundle.js


