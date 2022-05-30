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
HTTP interface to UnnaturalCode, and (transitivly) MITLM.

Currently only serves up a Python service.
"""

import shutil
import os

from api_utils import get_corpus_or_404, get_string_content
from flask import Flask, make_response, jsonify, Blueprint
from flask.ext.cors import cross_origin, CORS
from token_fmt import parse_tokens


app = unnaturalhttp = Blueprint('unnaturalcode-http', __name__)

#/ ROUTES /####################################################################
###############################################################################

@app.route('/<corpus_name>/')
def corpus_info(corpus_name):
    """
    GET /{corpus}/

    Retrieve a summary of the corpus info.
    """
    corpus = get_corpus_or_404(corpus_name)
    return jsonify(corpus.summary)


@app.route('/<corpus_name>/predict/',
        defaults={'token_str': ''}, methods=('POST',))
@app.route('/<corpus_name>/predict/<path:token_str>', methods=('GET',))
@cross_origin()
def predict(corpus_name, token_str=""):
    """
    POST /{corpus}/predict/{tokens*}
    POST /{corpus}/predict/f=?

    Returns a number of suggestions for the given token prefix.
    """
    corpus = get_corpus_or_404(corpus_name)

    if token_str:
        tokens = parse_tokens(token_str)
    else:
        tokens = corpus.tokenize(get_string_content())

    # Predict returns a nice, JSONable dictionary, so just return that.
    return jsonify(corpus.predict(tokens))


@app.route('/<corpus_name>/cross-entropy')
@app.route('/<corpus_name>/xentropy', methods=('GET', 'POST'))
@cross_origin()
def cross_entropy(corpus_name):
    """
    POST /{corpus}/xentropy/

    Calculate the cross-entropy of the uploaded file with respect to the
    corpus.
    """
    corpus = get_corpus_or_404(corpus_name)
    content = get_string_content()
    tokens = corpus.tokenize(content)
    return jsonify(cross_entropy=corpus.cross_entropy(tokens))

@app.route('/<corpus_name>/windowed-cross-entropy')
@app.route('/<corpus_name>/wxentropy', methods=('GET', 'POST'))
@cross_origin()
def windowed_cross_entropy(corpus_name):
    """
    POST /{corpus}/xentropy/

    Calculate the cross-entropy of the uploaded file with respect to the
    corpus.
    """
    corpus = get_corpus_or_404(corpus_name)
    content = get_string_content()
    tokens = corpus.tokenize(content)
    return jsonify(windowed_cross_entropy=corpus.windowed_cross_entropy(tokens))

@app.route('/<corpus_name>/', methods=('POST',))
def train(corpus_name):
    """
    POST /{corpus}/

    Upload a file for training.
    """
    corpus = get_corpus_or_404(corpus_name)
    content = get_string_content()
    tokens = corpus.tokenize(content)

    # NOTE: train doesn't really have a useful return...
    corpus.train(tokens)
    return make_response(jsonify(tokens=len(tokens)), 202)

@app.route('/<corpus_name>/', methods=('DELETE',))
def delete_corpus(corpus_name):
    corpus = get_corpus_or_404(corpus_name)

    assert hasattr(corpus, 'reset'), 'Python corpus MUST have a reset method!'
    if hasattr(corpus, 'reset'):
        corpus.reset()
    
    # Successful response with no content.
    return '', 204, {}


@app.route('/<corpus_name>/tokenize', methods=('POST',))
def tokenize(corpus_name):
    """
    POST /{corpus}/tokenize
    GET  /{corpus}/tokenize?s=...

    Tokenize the given string for this corpus's language.
    """
    corpus = get_corpus_or_404(corpus_name)
    # Args... should be a file or string
    content = get_string_content()
    return jsonify(tokens=corpus.tokenize(content, mid_line=False))

