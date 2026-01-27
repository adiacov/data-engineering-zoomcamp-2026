# Package all packages in the /modules directory at once
build-all:
	uv build --clear --all-packages
	