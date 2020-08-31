from flask import Flask, render_template
from control_parser import Parser

app = Flask(__name__)

file = open("sample_file", "r")
file_text = file.read().strip()
parser = Parser(file_text)

sorted_packages = sorted(parser.raw_pkg_info, key=lambda x: x['name'])
packages_dict = {pkg['name']: pkg for pkg in parser.clean_pkg_info }


@app.route('/')
def home():
    return render_template('top.html', package_list=sorted_packages)

@app.route('/<name>')
def show_package_info(name):
    return render_template('package.html', package=packages_dict[name])

@app.route('/favicon.ico') 
# Return something so the get request doesn't go to /<name> should have more specific paths
def favicon(): 
    return "placeholder"