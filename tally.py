import os
import re
import sys

import lxml.html
import requests


class RegexBuilder:

    @classmethod
    def prefix(cls):
        return r'(?:Number|No.|#)\s*'

    @classmethod
    def with_prefix_or_suffix(cls, regex, prefix, suffix):
        return r'(?:(?:%s)%s|%s(?:%s))' % (prefix, regex, regex, suffix)

    @classmethod
    def entry(cls, pattern):
        prefix = r'(?:Number|No.|#)\s*'
        suffix = r'#'
        return cls.with_prefix_or_suffix(pattern, prefix, suffix)

    @classmethod
    def suffix(cls):
        return r'\s*p(?:oin)?ts?'

    @classmethod
    def delimiter(cls):
        return r'[\s:=-]+'

    @classmethod
    def vote_splitter(cls):
        pattern = cls.entry(r'\d+') + cls.delimiter() + r'\d+' + cls.suffix()
        return re.compile(pattern, re.MULTILINE)

    @classmethod
    def score_splitter(cls):
        pattern = cls.entry(r'(\d+)') + cls.delimiter() + r'(\d+)' + cls.suffix()
        return re.compile(pattern)


class Vote:

    @staticmethod
    def tally(votes):
        result = {}
        for vote in votes:
            for entry, points in vote.points().items():
                result[entry] = result.get(entry, 0) + points
        return result

    def __init__(self, text):
        self.text = text

    def points(self):
        points = {}
        for score in re.findall(RegexBuilder.vote_splitter(), self.text):
            match = re.match(RegexBuilder.score_splitter(), score)
            if match:
                entry, score = [num for num in match.groups() if num is not None]
                points[entry] = int(score)
        if len(points) != 3:
            print >> sys.stderr, "Skipping: %s" % re.sub(r'\s+', ' ', self.text)
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
            paragraphs = html.cssselect('table.TopicReply td.Said p')
            scores = Vote.tally([Vote(tag.text_content()) for tag in paragraphs])
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
    except LookupError:
        app.usage()
    else:
        app.main(url)
