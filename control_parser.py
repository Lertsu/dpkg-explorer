# Control file parser, change to class at some point?
# Largely copying code from @aihaddad deb-parse https://github.com/aihaddad/deb-parse
import re
import os

#file = open("/var/lib/dpkg/status", "r")
#file_text = file.read()
#packages = file_text.split("\n\n")
class Parser:

    def __init__(self, text):
        packages = text.split("\n\n")
        
        self.raw_pkg_info = [self.get_raw_info(pkg) for pkg in packages]
        self.clean_pkg_info = [
            self.get_clean_info(pkg) for pkg in self.raw_pkg_info
        ]
        self.pkg_names = [pkg["name"] for pkg in self.raw_pkg_info]

    # makes package into a dictionary
    def get_raw_info(self, text):
        regex_splitter = re.compile(r"^[A-Za-z-]+:\s", flags=re.MULTILINE)
        keys = [key[:-2].lower() for key in regex_splitter.findall(text)]
        values = [value.strip() for value in re.split(regex_splitter,text)[1:]]

        if len(values) > 0:
            pkg_name = values[0]
            pkg_info = dict(zip(keys[1:], values[1:]))
            pkg_dict = {"name": pkg_name, "details": pkg_info}
            return pkg_dict
        #else:
            #raise ValueError("text is not in debian control format")

    def get_clean_info(self, raw_info):
        pkg_name = raw_info["name"]
        long_description = raw_info["details"]["description"]
        long_depends = raw_info["details"].get("depends")

        synopsis, description = self.split_description(long_description)
        depends, alt_depends = self.split_depends(long_depends)
        reverse_depends = self.get_reverse_depends(pkg_name, self.raw_pkg_info)
        pkg_details = {
            "synopsis": synopsis,
            "description": description,
            "depends": depends,
            "alt_depends": alt_depends,
            "reverse_depends": reverse_depends,
        }

        return {"name": pkg_name, "details": pkg_details}


    def split_description(self, long_description):
        if long_description is not None:
            split_description = tuple(long_description.split("\n", maxsplit=1))
            synopsis = split_description[0]
            description = (
                re.sub(r"^\s", "", split_description[1], flags=re.MULTILINE)
                if 1 < len(split_description)
                else None
            )
        else:
            synopsis, description = None, None

        return (synopsis, description)

    def split_depends(self, long_depends):
        if long_depends is not None:
            depends_and_alt = long_depends.split(" | ")
            depends = depends_and_alt[0].split(", ")
            alt_depends = (
                depends_and_alt[1].split(", ") if 1 < len(depends_and_alt) else None
            )
            depends = [re.sub("\(.*\)", "", x) for x in depends]
        else:
            depends, alt_depends = None, None

        return (depends, alt_depends)

    def get_reverse_depends(self, pkg_name, pkg_dict_list):
        r_depends = []
        for pkg in pkg_dict_list:
            pkg_depends = pkg["details"].get("depends")
            if pkg_depends is not None:
                if pkg_name in pkg_depends:
                    r_depends.append(pkg["name"])

        if len(r_depends) == 0:
            return None
        else:
            r_depends = [re.sub("\(.*\)", "", x) for x in r_depends]
        return None if len(r_depends) == 0 else r_depends
