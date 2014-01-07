import os
import re
import sys

import lxml.html
import requests


class Pattern:

    @classmethod
    def prefix(cls):
        return r'(?:Number|No.|#)\s*'

    @classmethod
    def with_prefix_or_suffix(cls, regex, prefix, suffix):
        return r'(?:(?:%s)%s|%s(?:%s))' % (prefix, regex, regex, suffix)

    @classmethod
    def entry(cls, capture = False):
        entry = r'(\d+)' if capture else r'\d+'
        prefix = r'(?:Number|No.|#)\s*'
        suffix = r'#'
        return cls.with_prefix_or_suffix(entry, prefix, suffix)

    @classmethod
    def suffix(cls):
        return r'\s*p(?:oin)?ts?'

    @classmethod
    def delimiter(cls):
        return r'[\s:=-]+'

    @classmethod
    def vote_splitter(cls):
        pattern = cls.entry() + cls.delimiter() + r'\d+' + cls.suffix()
        return re.compile(pattern, re.MULTILINE)

    @classmethod
    def score_splitter(cls):
        pattern = cls.entry(True) + cls.delimiter() + r'(\d+)' + cls.suffix()
        return re.compile(pattern)


class Vote:

    @staticmethod
    def tally(votes):
        result = {}
        for vote in votes:
            for entry, points in vote.points().items():
                result[entry] = result.setdefault(entry, 0) + points
        return result

    def __init__(self, text):
        self.text = text

    def points(self):
        points = {}
        for score in re.findall(Pattern.vote_splitter(), self.text):
            match = re.match(Pattern.score_splitter(), score)
            if match:
                entry, score = [num for num in match.groups() if num is not None]
                points[entry] = int(score)
        if len(points) != 3:
            message = "Skipping message: %s\n" % re.sub(r'\s+', ' ', self.text)
            sys.stderr.write(message)
            return {}
        else:
            return points


class App:

    def usage(self):
        script = os.path.basename(sys.argv[0])
        sys.stderr.write("Usage: %s <discussion-html>\n" % script)
        sys.exit(1)

    def main(self, url):
        response = requests.get(url)
        if response.ok:
            html = lxml.html.fromstring(response.text)
            messages = html.cssselect('table.TopicReply td.Said p')
            votes = [Vote(message.text_content()) for message in messages]
            scores = Vote.tally(votes)
            results = sorted(scores, key = scores.get, reverse = True)
            print "\nRESULTS\n======="
            for entry in results:
                print "#%s - %d points" % (entry, scores[entry])
        else:
            sys.stderr.write(response.text + "\n")


if __name__ == '__main__':
    app = App()
    try:
        url = sys.argv[1]
        App().main(url)
    except LookupError:
        app.usage()
