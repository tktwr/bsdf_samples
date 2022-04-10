WIN_HOME=C:/Users/$(USER)
ADDONS_DIR=$(WIN_HOME)/AppData/Roaming/Blender Foundation/Blender/3.1/scripts/addons
ADDON_NAME=bsdf_samples

all:

upload:
	cp -a $(ADDON_NAME) "$(ADDONS_DIR)"

diff:
	vimdiff.sh "$(ADDONS_DIR)/$(ADDON_NAME)/__init__.py" $(ADDON_NAME)/__init__.py

dirdiff:
	vimdirdiff.sh "$(ADDONS_DIR)/$(ADDON_NAME)" $(ADDON_NAME)

.PHONY: pkg
pkg:
	./bin/make_zip.sh $(ADDON_NAME) pkg

clean:
	rm -rf pkg
