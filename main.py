import re
import ssl
import sys
import html
import urllib
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError, HTTPError

results = []
targeturl = ''

def init():

    global targeturl
    args = sys.argv[0:]
    optionLen = len(args)

    # e.g.: python main.py -t https://aws.amazon.com
    for i in range(optionLen-1):
        if args[i].upper() == '-T':	# -T: target URL
            data = str(args[i+1])
            targeturl = data
    if targeturl == '':
        print ('[ERR] Please be sure to include the target url.')
        return False

    return True

def main():

    if init():
        context = ssl._create_unverified_context()
        useragent = 'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
        tu = targeturl
        validLanguages =\
            ['Deutsch', 'Espa&ntilde;ol', 'Fran&ccedil;ais', 'Italiano', 'Portugu&ecirc;s',\
            'T&uuml;rk&ccedil;e', 'Ρусский', '日本', '한국', '中文',\
            '简体', '繁體']
            # Other languages
            #'Bahasa Indonesia', 'español', 'Español (América Latina)', 'français', 'Português Brasileiro', 'Tiếng Việt', 'Türkçe', 'Русский', 'ภาษาไทย'

        try:
            req = Request(tu)
            req.add_header('User-Agent', useragent)

            with urlopen(req, context=context) as response:
                htmlPage = response.read().decode("utf-8")
        except HTTPError as e:
            code = str(e.code)
            print('\n[ERR] HTTP Error: The server couldn\'t fulfill the request to\n%s\n+ Error Code: %s' %(tu, code))
            return False
        except URLError as e:
            code = e.reason
            print('\n[ERR] URL Error: We failed to reach in\n%s\n+ Error Code: %s' %(tu, code))
            return False

        body = re.search('<body.*/body>', htmlPage, re.I|re.S)
        body = body.group()
        body = re.sub('<script.*?>.*?</script>', ' ', body, 0, re.I|re.S)
        body = body.\
            replace('<form', '|<form').replace('form>', 'form>|').\
            replace('<p', '|<p').replace('p>', 'p>|').\
            replace('<ul', '|<ul').replace('ul>', 'ul>|').\
            replace('<li', '~<li').replace('li>', 'li>~').\
            replace('<option', '~<option').replace('option>', 'option>~')
        #print (body)
        body = re.sub('<.+?>', '', body, 0, re.I|re.S)
        body = " ".join(body.split())
        #print (body)
        tokens = body.split('|')
        tokens = [x.strip() for x in tokens if x.strip()]
        #print (tokens)

        for token in tokens:
            token = html.unescape(token)
            if token.find('English') >= 0:
                for validLanguage in validLanguages:
                    if token.find(validLanguage) >= 0:
                        results.append(token)
                        break

        if len(results) > 0:
            result = results[0].split('~')
            result = [x.strip() for x in result if x.strip()]
            #result = list(set(result))
            count = len(result)
            if count > 0:
                print (result)
                print ('[OK] This site supports %d languages. @%s' %(count, tu))
                return True
            else:
                return False
        else:
            print ('[ERR] The target URL you requested can\'t find the language data it supports.\n+ It means that the target site only supports one language.')
            return False
    else:
        print ('[ERR] Initialization failure')
        return False

if __name__ == '__main__':
    print ('[END] Command returned %d' %int(main()))
