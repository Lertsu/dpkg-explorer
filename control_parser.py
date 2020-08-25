file = open("/var/lib/dpkg/status", "r")

def parse_file(file):
    file_text = file.read()
    packages = file_text.split("\n\n")
    print(packages[0])
