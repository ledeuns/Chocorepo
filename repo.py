#! /usr/bin/env python
"""Creates an OData service from weather data"""

REPO_DB = 'dbrepo.db'
STREAM_DB = 'dbstream.db'

SERVICE_PORT = 8080
SERVICE_ROOT = "http://chocopkg/"
SERVE_ADDRESS = "127.0.0.1"

import logging
import time
import string
import os
import StringIO
import os.path
from wsgiref.simple_server import make_server

import pyslet.iso8601 as iso
import pyslet.odata2.csdl as edm
import pyslet.odata2.core as core
import pyslet.odata2.metadata as edmx
import pyslet.http.params as params
from pyslet.odata2.server import ReadOnlyServer
from pyslet.odata2.sqlds import *
#from pyslet.odata2.memds import InMemoryEntityContainer
import pyslet.http.client as http

class FindPackagesByIdFunctionCollection(core.FunctionEntityCollection):
    def __init__(self,function,params,pkgEntitySet):
        core.FunctionEntityCollection.__init__(self,function,params)
        self.id=params['id']
        self.collection=self.entitySet.OpenCollection()

    def itervalues(self):
        return self.order_entities(
         self.expand_entities(self.filter_entities(
         self.generate_entities())))

    def generate_entities(self):
        for p in self.collection:
            if self.collection[p].get('Id').value == self.id:
                yield self.collection[p]

class SearchFunctionCollection(core.FunctionEntityCollection):                                             
    def __init__(self,function,params,pkgEntitySet):
        core.FunctionEntityCollection.__init__(self,function,params)
	self.searchterm=params['searchTerm']
        self.collection=self.entitySet.OpenCollection()

    def itervalues(self):
        #self.set_filter(core.CommonExpression.from_str("contains(Id,'%s')" %(self.searchTerm)))
        return self.order_entities(
         self.expand_entities(self.filter_entities(
         self.generate_entities())))

    def generate_entities(self):
        for p in self.collection:
                yield self.collection[p]

def LoadMetadata(path=os.path.join(os.path.split(__file__)[0],'metadata.xml')):
    """Loads the metadata file from the current directory."""
    doc = edmx.Document()
    with open(path, 'rb') as f:
        doc.Read(f)
    return doc

def MakeContainer(doc, drop=False, path=REPO_DB):
    if drop and os.path.isfile(path):
        os.remove(path)
    create = not os.path.isfile(path)
    container = SQLiteEntityContainer(
        file_path=path,
        container=doc.root.DataServices['NuGetGallery.FeedContext_x0060_1'],
        streamstore=SQLiteStreamStore(file_path=STREAM_DB, dpath='/home/chocorepo/pkg'))
    if create:
        container.create_all_tables()

    searchFunc=doc.root.DataServices['NuGetGallery.FeedContext_x0060_1.Search']
    searchFunc.bind(SearchFunctionCollection, pkgEntitySet=doc.root.DataServices['NuGetGallery.FeedContext_x0060_1.Packages'])
    findPackagesByIdFunc=doc.root.DataServices['NuGetGallery.FeedContext_x0060_1.FindPackagesById']
    findPackagesByIdFunc.bind(FindPackagesByIdFunctionCollection, pkgEntitySet=doc.root.DataServices['NuGetGallery.FeedContext_x0060_1.Packages'])

    return doc.root.DataServices['NuGetGallery.FeedContext_x0060_1']


def main():
    """Executed when we are launched"""
    doc = LoadMetadata()
    container = MakeContainer(doc)
    server = ReadOnlyServer(serviceRoot=SERVICE_ROOT)
    server.SetModel(doc)

    srv = make_server(SERVE_ADDRESS, SERVICE_PORT, server)
    logging.info("HTTP server on port %i running" % SERVICE_PORT)
    srv.serve_forever()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
