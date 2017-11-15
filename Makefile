.PHONY: test
test:
	@tox

build:
	@charm build -rl DEBUG

clean:
	@rm -rf `echo $(JUJU_REPOSITORY)`/builds/filebeat
