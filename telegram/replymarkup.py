#!/usr/bin/env python3


class ReplyMarkup(object):
    def to_json(self):
        raise NotImplementedError

    def __str__(self):
        return self.to_json()
