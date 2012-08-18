templates:
	echo "module.exports = " > pecan.js/templates.js
	node build_templates.js >> pecan.js/templates.js

build:
	npm install
	make templates
	cd node_modules/plate/ && make build && cd -
	cat node_modules/plate/plate.min.js > src/media/js/bundle.js
	cat pecan.js/jquery.js >> src/media/js/bundle.js
	node_modules/.bin/browserify pecan.js/site.js >> src/media/js/bundle.js


