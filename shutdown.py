from sys import argv

try:
	from Utils.funcs import forceQuitUnveillance
except ImportError as e:
	if DEBUG: print e
	from lib.Frontend.Utils.funcs import forceQuitUnveillance

if __name__ == "__main__":
	target = argv[1].split("/")[-1].replace(".py", "")
	forceQuitUnveillance(target=target)