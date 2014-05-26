#!/usr/bin/env python

# PassPack "export to CSV" default format:
# Name,User ID,Password,Link,Tags,Notes,Email

import sys
import csv
from datetime import datetime as dt

_VERSION = 1.0
_BANNER = "KeePassPack %s" % _VERSION

_USAGE = """Converts PassPack CSV output to KeePassX XML.

Usage: ./keepasspack.py <csv input file> [xml output file]
       ./keepasspack.py -i [xml output file]

The -i option reads CSV data from user input. Since the default output from
PassPack is copied to the clipboard, it can be easily pasted here.
       
If the output file is not specified, output is saved to "output.xml" in the
current directory.
"""    


def display_usage():
    print _USAGE
    sys.exit()


def timestamp():
    h = dt.now().hour
    m = dt.now().minute
    s = dt.now().second
    y = dt.now().year
    month = dt.now().month
    d = dt.now().day
    
    stamp = "%04d-%02d-%02dT%02d:%02d:%02d" % (y, month, d, h, m, s)
    return stamp


def csv_input_to_list():
    """Reads PassPack CSV exported data and returns a list of dictionaries.
    """
    
    csv_input = ""
    
    while True:
        try:
            csv_input += raw_input()
            csv_input += "\n"
        except EOFError:
            break
        
    return csv_to_list(csv_input.split("\n"))


def csv_file_to_list(csv_filename):    
    csv_file = open(csv_filename, 'rb')

    return csv_to_list(csv_file)


def csv_to_list(csv_file):
    """Takes a file or list object containing PassPack exported CSV data and 
    returns a list containing one dictionary per entry.
    """
    
    passpack_csv_fields = ["name", "user_id", "password", "link", "tags",
                           "notes", "email"]
                           
    csv_reader = csv.DictReader(csv_file, fieldnames=passpack_csv_fields)

    output_list = []    
    for entry in csv_reader:
        output_list.append(entry)

    return output_list
    

def xml_safe(s):
    """Returns the XML-safe version of a given string.
    """
    
    new_string = s.replace("&", "&amp;").replace("<", "&lt;")
    new_string = new_string.replace("\r", "").replace("\n", "<br/>")
    return new_string


def entry_dict_to_xml(entry):
    """Takes an entry stored in a dictionary and returns entry as a KeePassX
    XML formatted string.
    """
    
    if entry["email"].strip() != "":
        comment = "Email: %s<br/>" % xml_safe(entry["email"])
    else:
        comment = ""
        
    comment += xml_safe(entry["notes"])

    if entry["tags"].strip() != "":
        comment += "<br/>Tags: %s" % xml_safe(entry["tags"])

    creation_date = timestamp()

    xml_entry = """
   <entry>
    <title>%(title)s</title>
    <username>%(username)s</username>
    <password>%(password)s</password>
    <url>%(url)s</url>
    <comment>%(comment)s</comment>
    <icon>0</icon>
    <creation>%(creation)s</creation>
    <lastaccess>%(lastaccess)s</lastaccess>
    <lastmod>%(lastmod)s</lastmod>
    <expire>Never</expire>
   </entry>    
    """ % { "title": xml_safe(entry["name"]),
            "username": xml_safe(entry["user_id"]),
            "password": xml_safe(entry["password"]),
            "url": xml_safe(entry["link"]),
            "comment": comment,
            "creation": creation_date,
            "lastaccess": creation_date,
            "lastmod": creation_date,
          }
    
    return xml_entry
    

def main():
    print "=" * len(_BANNER)
    print _BANNER
    print "=" * len(_BANNER)
    
    if len(sys.argv) <= 1: display_usage()
    elif sys.argv[1] == "-h" or sys.argv[1] == "--help": display_usage()

    csv_filename = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_filename = sys.argv[2]
    else:
        output_filename = "output.xml"


    if csv_filename == "-i":
        print "Reading entries from user input."
        print "Press CTRL+D on a blank line when done."
        entries_list = csv_input_to_list()
    else:
        print "Reading entries from PassPack CSV export: %s..." % csv_filename   
        entries_list = csv_file_to_list(csv_filename)

    print "%d entries found." % len(entries_list)

    xml_head = """<!DOCTYPE KEEPASSX_DATABASE>
<database>
 <group>
  <title>PassPack Imported Entries</title>
  <icon>0</icon>
"""

    xml_tail = """ </group>
</database>"""

    xml_output = xml_head

    for entry in entries_list:
        xml_output += entry_dict_to_xml(entry)
        
    xml_output += xml_tail
    
    output_file = open(output_filename, 'w')
    output_file.write(xml_output)
    output_file.close()
    
    print "Output saved to: %s" % output_filename

    
if __name__ == "__main__":
    main()
