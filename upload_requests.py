import sys                          #for command-line arguments
import os                           #for dealing with filepaths properly
import requests
from urllib import parse            #for urlencode
import getpass                      #password reading from commandline
from bs4 import BeautifulSoup                     #for parsing and (re-)generating html5
#import urllib
#------ SETTINGS -------#
LOGIN_URL = "http://igem.org/Login2"
#DO NOT end base url with "/"
TEAM_NAME = "Aalto-Helsinki"
IGEM_BASE = "http://2016.igem.org"
LOGIN_BASE_URL = IGEM_BASE+"/Team:"+TEAM_NAME
BASE_URL = IGEM_BASE+"/wiki/index.php?title=Team:"+TEAM_NAME
FILE_BASE_URL = IGEM_BASE+"/File:T--"+TEAM_NAME+"--"
TEMPLATE_BASE_URL = IGEM_BASE+"/wiki/index.php?title=Template:"+TEAM_NAME+"--"
UPLOAD_URL = IGEM_BASE+"/Special:Upload"
AUTO_PAGES = ["index","Business","Research","Team","Journal","Modeling","Cooperation","Outreach"]
#-----------------------#

# Wrangler class - parser object which parses HTML
from html.parser import HTMLParser
class Wrangler(HTMLParser):
    #The tags, a.k.a. id's are stored here. For example wpEditToken
    ids = {}
    #Method which handles every start tag eg. <input>
    def handle_starttag(self, tag, attrs):
        if (tag == 'input'):
            for i in attrs:
                if (i[0] == 'name'):
                    if (i[1] != None and i[1] != 'wpPreview' and i[1] != 'wpDiff'):
                        name = i[1]
                        value_tag = [c for c in attrs if c[0]=='value']
                        if value_tag:
                            value = value_tag[0][1]
                            self.ids[name]=value

def replace_property_of_tags_with_function_return_value_in_file(property, tag, function, filepath, parameters = None):
    soup = BeautifulSoup(open(filepath), "html5lib")
    for tag in soup.find_all(tag):
        property_value = tag[property]
        if (parameters == None): return_val = function(property_value)
        else: return_val = function(property_value, parameters)
        tag[property] = return_val
    return soup.prettify().encode("utf8")

def replace_img_tags(filepath, session):
    return replace_property_of_tags_with_function_return_value_in_file('src', 'img', image_upload, filepath, session)
	
def replace_script_tags(filepath, session):
    return replace_property_of_tags_with_function_return_value_in_file('src', 'script', js_upload, filepath, session)
	
def replace_link_tags(filepath, session):
    return replace_property_of_tags_with_function_return_value_in_file('href', 'link', css_upload, filepath, session)

def get_image_tags(file, session):
    soup = BeautifulSoup(open(file), "html5lib")
    for tag in soup.find_all("img"):
        image_path = tag['src']
        link = image_upload(image_path, session)
        tag['src'] = link
    return soup.prettify().encode("utf8")
	
def get_edit_parameters(url, session):
    try:
        resp = session.get(url)
        content = resp.text
        parser = Wrangler()
        parser.ids = {}
        parser.feed(content)
        return parser.ids
    except:
        print("Error:", sys.exc_info()[0])
        return None

def relative_from_absolute_path(absolutepath):
    thispath = os.path.realpath('.').split(os.sep)[-1]
    return absolutepath.split(thispath)[-1].lstrip("/")

def get_filename_from_path(filepath):
    return filepath[filepath.rfind("/")+1:]

def read_image_file(filepath):
    try:
        relativepath = relative_from_absolute_path(filepath)
        filename = get_filename_from_path(filepath)
        filetype = filename[filename.rfind(".")+1:]
        return {'wpUploadFile': (filename, open(relativepath, "rb"), "image/"+filetype)}
        #print(image_file)
    except FileNotFoundError:
        print("File " + filepath + " not found.")
        return None

def send_file_to_server( image_file, data, session, url = UPLOAD_URL ):
    try:
        # Post to Special:Upload
        filename = image_file['wpUploadFile'][0]
        data['wpDestFile'] = "T--"+TEAM_NAME+"--"+filename
        data['wpIgnoreWarning'] = '0'
        print("T--"+TEAM_NAME+"--"+filename)
        #resp = requests.post( UPLOAD_URL, data=data, files=image_file, cookies=session.cookies)
        return requests.post( UPLOAD_URL, data=data, files=image_file, cookies=session.cookies)
        #print(resp.content)
    except:
        print("Error sending file to server")
        return None

def get_link_to_file(response):
    try:
        soup = BeautifulSoup(response.text, "html5lib")
        print(soup.find(class_="fullImageLink").a.get("href"))
        return soup.find(class_="fullImageLink").a.get("href")
    except:
        print("Error parsing response to find image link, ", sys.exc_info()[0])
        return None

def template_upload_in_tags(filepath, tag, session):
    filename = get_filename_from_path(filepath)
	url = TEMPLATE_BASE_URL+filename
    data = get_edit_parameters(url+"&action=edit", session)
    if (data == None): return 1

    css_data = read_css_file(filepath)
    if (css_file == None): return 2
    css_data = "<html><"+tag+">"+css_data+"</"+tag+"></html>"

    response = send_html_to_server(url+"&action=submit", css_data, data, session)
    if (response == None): return 3

    return url

def js_upload(filepath, session):
    return template_upload_in_tags(filepath, "script", session)

def read_file(filepath):
    try:
        with open (filepath, "r", encoding="utf8") as myfile:
            file_data=myfile.read()
    except FileNotFoundError:
        #print("File {:s} not found".format(file))
        print("File " + filepath + " not found.")
        return None
    return "<html><style>"+file_data+"</style></html>"
	
def css_upload(filepath, session):
    return template_upload_in_tags(filepath, "style", session)
	
def image_upload(file, session):
    # Get edit id
    data = get_edit_parameters(UPLOAD_URL, session)
    if (data == None): return 1
    
    # Read file
    image_file = read_image_file(file)
    if (image_file == None): return 2

    # Send file to iGEM server
    response = send_file_to_server(image_file, data, session)
    if (response == None): return 3

    # Return link to file
    link = get_link_to_file(response)
    if (link == None): return 4
    return link

def headerfooter():
#---- read header & footer ---#
    if (headerfooter == True):
        try:
            with open ("include/header.html", "r") as myfile:
                header_data=myfile.read()
        except FileNotFoundError:
            print("no include/header.html found. Not including")
            header_data = ""

        try:
            with open ("include/footer.html", "r") as myfile:
                footer_data=myfile.read()
        except FileNotFoundError:
            print("no include/footer.html found. Not including")
            footer_data = ""

        file_data = header_data+file_data+footer_data

def send_html_to_server(url, html_data, parameters, session):
    try:
        parameters['wpTextbox1'] = html_data
        return requests.post(url, data=parameters, cookies=session.cookies)
    except:
        print("Error:", sys.exc_info()[0])
        return None

def upload(page, file, session, headerfooter = False):
    #---- read requested file ----#
    try:
        file_data = get_image_tags(file, session)
        #soup = BeautifulSoup(open(file), "html5lib")
        #file_data = soup.prettify().encode("utf8")
        #print(file_data)
    except:
        print("Error:", sys.exc_info()[0])
        return 1
    
    if (page == "index"):
        data = get_edit_parameters(BASE_URL+"&action=edit", session)
    else:
        data = get_edit_parameters(BASE_URL+"/"+page+"&action=edit", session)
    if (data == None): return 2

    #------- post new edit -------#
    if (page == "index"):
        resp = send_html_to_server(BASE_URL+"&action=submit", file_data, data, session)
    else:
        resp = send_html_to_server(BASE_URL+"/"+page+"&action=submit", file_data, data, session)
    if (resp == None): return 3

    return 0


def login( username, password):
    #---------- log in------------#
    try:
        login_data = {'return_to':LOGIN_BASE_URL,'username':username,'password':password,'Login':'Login'}
        s = requests.session()
        resp = s.post(LOGIN_URL, login_data)
        return s
    except urllib.error.URLError:
        print("Login server not found. Perhaps the URL is wrong in the code?")
        return 1
    except:
        print("Error:", sys.exc_info()[0])
        return 1
    return 0


def main(argv=sys.argv):
    #----- arguments -------------#
    try:
        if (argv[1] != '-auto'):
            page = argv[1]
            file = argv[2]
    except IndexError:
        print("Usage: upload.py wikipage filename\n\nwikipage\tThe subpage in the wiki.\n\t\teg. in igem.org/wiki/index.php?title=Team:teamname/members\n\t\twikipage=members\n\nfile\t\tfilename in current directory")
        return

    #------- read input ----------#
    try:
        print("-- iGEM wiki quickify --\ncmd + d to abort.")
        username = input("Username: ")
        username = username.encode("utf8")
        password = getpass.getpass('Password: ')
        #input("Password: ")
    except EOFError:
        print("Aborting...")
        return 1
    print("Logging in")
    login_result = login(username, password)
    if (login_result == 2):
        print("Invalid username/password")
        return 1
    #elif (login_result != 0):
    #    print("Server error when logging in")
    #    return 1
    #------- automation ---------#
    if (argv[1] == '-auto'):
        print("Auto updating pages: ",",".join(AUTO_PAGES))
        for p in AUTO_PAGES:
            r=upload(p,p+".html", login_result, True)
            if (r == 2):
                print("{:s}.html\t\tFile not found".format(p))
            elif (r== 1):
                print("{:s}.html\t\tServer error".format(p))
            elif (r== 3):
                print("{:s}.html\t\tUnknown error".format(p))
            else:
                print("{:s}.html\t\tUploaded".format(p))
    else:
        print("Uploading contents of \"{:s}\" to \"{:s}\"".format(file, page))
        r = upload( page, file, login_result)
        if (r == 2):
            print("{:s}.html\t\tFile not found".format(file))
        elif (r != 0):
            print("Error occured")
    print("Done")


main()
