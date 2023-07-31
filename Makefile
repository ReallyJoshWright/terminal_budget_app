DIRS = . src config files images
CACHEDIRS = $(foreach D, $(DIRS), $(wildcard $(D)/*__pycache__))

all:

.PHONY: clean cleandb
clean:
	rm -rf $(CACHEDIRS)
cleandb:
	rm -rf config/account.db
	@cat config/account.sql | sqlite3 config/account.db
	@cat config/balance.sql | sqlite3 config/account.db
