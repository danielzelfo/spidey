""" robotparser.py

    Copyright (C) 2000  Bastian Kleineidam

    You can choose between two licenses when using this package:
    1) GNU GPLv2
    2) PSF license for Python 2.2

    The robots.txt Exclusion Protocol is implemented as specified in
    http://www.robotstxt.org/norobots-rfc.txt
"""

import urllib.parse
import urllib.request
import re


class RuleLine:
    """A rule line is a single "Allow:" (allowance==True) or "Disallow:"
       (allowance==False) followed by a path."""
    def __init__(self, path, allowance):
        if path == '' and not allowance:
            # an empty value means allow all
            allowance = True
        path = urllib.parse.urlunparse(urllib.parse.urlparse(path))
        self.path = path#urllib.parse.quote(path)
        self.allowance = allowance

    def applies_to(self, filename):
        pattern = re.escape(self.path+"*").replace(r"\*", ".*").replace(r"\$", "$").replace(r"\^", "^")
        return bool(re.match(pattern, filename))
        #return self.path == "*" or filename.startswith(self.path)

    def __str__(self):
        return ("Allow" if self.allowance else "Disallow") + ": " + self.path


class Entry:
    """An entry has one or more user-agents and zero or more rulelines"""
    def __init__(self):
        self.useragents = []
        self.rulelines = []
        self.delay = None
        self.req_rate = None

    def __str__(self):
        ret = []
        for agent in self.useragents:
            ret.append(f"User-agent: {agent}")
        if self.delay is not None:
            ret.append(f"Crawl-delay: {self.delay}")
        if self.req_rate is not None:
            rate = self.req_rate
            ret.append(f"Request-rate: {rate.requests}/{rate.seconds}")
        ret.extend(map(str, self.rulelines))
        return '\n'.join(ret)

    def applies_to(self, useragent):
        """check if this entry applies to the specified agent"""
        # split the name token and make it lower case
        useragent = useragent.split("/")[0].lower()
        for agent in self.useragents:
            if agent == '*':
                # we have the catch-all agent
                return True
            agent = agent.lower()
            if agent in useragent:
                return True
        return False

    def allowance(self, filename):
        """Preconditions:
        - our agent applies to this entry
        - filename is URL decoded"""
        wasDisAllowed = False
        for line in self.rulelines:
            if line.applies_to(filename):
                if line.allowance:
                    return True
                else:
                    wasDisAllowed = True
        return not wasDisAllowed
