.PHONY: all
all: slides.html

.PHONY: clean
clean:
	rm slides.html

slides.html: remark-template.bash slides.md
	./remark-template.bash "GRACE Groundwater Exploration Slides" "$$(cat ./slides.md)" > $@
