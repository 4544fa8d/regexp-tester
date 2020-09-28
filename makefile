uninstall:
	rm /usr/bin/regexp-tester

install: uninstall
	cp ./regexp-tester.py /usr/bin/regexp-tester
	chmod +x /usr/bin/regexp-tester
