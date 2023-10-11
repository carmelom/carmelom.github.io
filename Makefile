.PHONY: serve print

serve:
	browser-sync start --server --port 9997 -f -w

print:
	C:\Program Files\Google\Chrome\Application\chrome.exe --headless --disable-gpu --print-to-pdf=cv.pdf cv.html
