#!/usr/bin/env python

# Copyright (C) 2014  Eddie Antonio Santos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



"""
Defines corpus object(s).
Currently, only PythonCorpus is defined.
"""

import os
import shutil

from unnaturalcode import ucUser

from flask.json import loads as unjson

__all__ = ['PythonCorpus', 'CORPORA', 'GenericCorpus']

# See "On Naturalness of Software", Hindle et al. 2012
BEHINDLE_NGRAM_ORDER = 6
GOOD_ENOUGH_NGRAM_ORDER = 4
CAMPBELL_NGRAM_ORDER = 10

class GenericCorpus(object):
    """
    The default UnnaturalCode Python corpus.
    """

    name = 'Generic corpus_name [MITLM]'
    description = __doc__
    language = 'Generic'

    # Get the singleton instance of the underlying Python language (source)
    # model.
    # [sigh]... this API.
    _user = ucUser.genericUser(ngram_order=CAMPBELL_NGRAM_ORDER)
    _sourceModel = _user.sm
    _lang = _sourceModel.lang()
    _mitlm = _sourceModel.cm

    order = _mitlm.order
    # Hard-coded because "it's the best! the best a language model can get!"
    smoothing = 'ModKN'

    def __init__(self):
        self.last_updated = None

    @property
    def summary(self):
        "Returns a select portion of properties."

        props = ('name', 'description', 'language', 'order', 'smoothing',
                 'last_updated')
        return {attr: getattr(self, attr) for attr in props}

    def tokenize(self, string, mid_line=True):
        """
        Tokenizes the given string in the manner appropriate for this
        corpus's language model.
        """
        return self._sourceModel.lang(unjson(string))

    def train(self, tokens):
        """
        Trains the language model with tokens -- precious tokens!
        Updates last_updated as a side-effect.
        """
        returnv = self._sourceModel.trainLexemes(tokens)
        self._mitlm.stopMitlm()
        return returnv

    def predict(self, tokens):
        """
        Returns a dict of:
            * suggestions: a list of suggestions from the given token string.
            * tokens: the actual list of tokens used in the prediction. Note
                      that this may be different from the given input.
        """

        # The model *requires* at least four tokens, so pad prefixs tokens
        # with `unks` until it works.
        if len(tokens) < self.order:
            unk_padding_size = self.order - len(tokens)
            prefix_tokens = [[None, None, None, None, '<unk>']] * unk_padding_size
        else:
            prefix_tokens = []
        prefix_tokens.extend(tokens)

        # Truncate to the n-gram order size, because those are all the tokens
        # that you really need for prediction...
        prefix_tokens = prefix_tokens[-self.order:]

        return {
            'suggestions': self._sourceModel.predictLexed(prefix_tokens),
            'tokens': prefix_tokens
        }

    def cross_entropy(self, tokens):
        """
        Calculates the cross entropy for the given token string.
        """
        return self._sourceModel.queryLexed(tokens)

    def windowed_cross_entropy(self, tokens):
        """
        Calculates the cross entropy for the given token string.
        """
        return self._sourceModel.windowedQuery(tokens, returnWindows=False)

    def reset(self):
        # Ask MITLM politely to relinquish its resources and halt.
        self._mitlm.release()
        self._user.delete()

    def __del__(self):
        # Ensures that MITLM has stopped.
        self._mitlm.release()


class PythonCorpus(GenericCorpus):
    """
    The default UnnaturalCode Python corpus.
    """

    name = 'Python corpus_name [MITLM]'
    description = __doc__
    language = 'Python'

    # Get the singleton instance of the underlying Python language (source)
    # model.
    # [sigh]... this API.
    _user = ucUser.pyUser(ngram_order=GOOD_ENOUGH_NGRAM_ORDER)
    _sourceModel = _user.sm
    _lang = _sourceModel.lang()
    _mitlm = _sourceModel.cm

    order = _mitlm.order
    # Hard-coded because "it's the best! the best a language model can get!"
    smoothing = 'ModKN'

    def tokenize(self, string, mid_line=True):
        """
        Tokenizes the given string in the manner appropriate for this
        corpus's language model.
        """
        return self._lang.lex(string, mid_line)

CORPORA = {
    'py': PythonCorpus(),
    'generic' : GenericCorpus()
}
