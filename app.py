#!/usr/bin/env python

import os
import sys
import json
import requests
from collections import defaultdict


class GitHub:
    rest_url = 'https://api.github.com'
    graphql_url = 'https://api.github.com/graphql'
    _headers = {
        'Authorization': 'token %s' % os.getenv('API_TOKEN'),
        'User-Agent': os.getenv('USER_AGENT', 'Asyncy')
    }

    @staticmethod
    def _query(url, method, *args, **kwargs):
        res = getattr(requests, method)(
            GitHub.graphql_url, *args,
            headers=GitHub._headers, **kwargs
        )
        try:
            res.raise_for_status()
        except:
            sys.stderr.write(res.text)
            raise
        else:
            return res.json()

    @staticmethod
    def languages(login, repos=10, languages=3):
        query = """query {
          user(login: "%s") {
            repositories(first:%s) {
              nodes {
                languages(first:%s) {
                  nodes {
                    name
                  }
                }
              }
            }
          }
        }""" % (login, repos, languages)

        res = GitHub._query(
            GitHub.graphql_url, 'post',
            json.dumps({'query': query})
        )

        # create a dict of results
        languages = defaultdict(int)

        # loop through the graphql results
        for node in res['data']['user']['repositories']['nodes']:
            for language in node['languages']['nodes']:
                languages[language['name']] += 1

        # sort by popularity
        languages = sorted(
            languages.items(),
            key=lambda a: a[1],
            reverse=True
        )

        # pop our the languages into a list
        return list(map(lambda l: l[0], languages))


if __name__ == '__main__':
    sys.stdout.write(json.dumps(getattr(GitHub, sys.argv[1])(*sys.argv[2:])))
