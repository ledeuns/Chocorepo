import sqlite3
import os
import zipfile
import shutil
import sys
import datetime
import hashlib
from xml.dom import minidom

hmd5 = hashlib.md5()
hsha256 = hashlib.sha256()

with open(sys.argv[1], 'rb') as f:
    ablob = f.read()
    if len(ablob):
        hmd5.update(ablob)
        hsha256.update(ablob)

db = sqlite3.connect('dbstream.db')
with db:
    c = db.cursor()
    c.execute('SELECT MAX(s.streamid), MAX(bl.blockid) FROM streams s, blocklists bl;')
    cres = c.fetchone()
    cursid = cres[0]
    curblid = cres[1]
    if cursid is None:
        cursid = 0
    if curblid is None:
        curblid = 0
    blockid = curblid+1
    streamid = cursid+1
    c.close()

    fsize = os.path.getsize(sys.argv[1])
    if fsize > 65536:
        raise Exception("File too big")

    # CREATE TABLE "Streams" ("streamID" INTEGER NOT NULL, "mimetype" TEXT NOT NULL, "created" TIMESTAMP NOT NULL, "modified" TIMESTAMP NOT NULL, "size" INTEGER NOT NULL, "md5" BLOB, PRIMARY KEY ("streamID"));
    db.execute('INSERT INTO Streams VALUES(?, ?, ?, ?, ?, ?)', [streamid, "application/zip", datetime.datetime.now(), datetime.datetime.now(), os.path.getsize(sys.argv[1]), buffer(hmd5.digest())])
    # CREATE TABLE "BlockLists" ("blockID" INTEGER NOT NULL, "num" INTEGER NOT NULL, "hash" TEXT NOT NULL, "StreamsBlockLists_streamID" INTEGER, PRIMARY KEY ("blockID"), CONSTRAINT "StreamsBlockLists" FOREIGN KEY ("StreamsBlockLists_streamID") REFERENCES "Streams"("streamID"));
    db.execute('INSERT INTO BlockLists VALUES(?, ?, ?, ?)', [blockid, 1, hmd5.hexdigest(), streamid])
    # CREATE TABLE "Blocks" ("hash" TEXT NOT NULL, "data" BLOB NOT NULL, PRIMARY KEY ("hash"));
    db.execute('INSERT INTO Blocks VALUES(?, ?)', [hmd5.hexdigest(), buffer(ablob)])
    db.commit()

fdir = "pkg/"+hmd5.hexdigest()[:2]+"/"+hmd5.hexdigest()[2:4]

if not os.path.exists(fdir):
    os.makedirs(fdir)

shutil.copy(sys.argv[1], fdir+"/"+hmd5.hexdigest()[4:])

with zipfile.ZipFile(sys.argv[1]) as z:
    xmldoc = minidom.parse(z.open("_rels/.rels"))
    pkgtarget = xmldoc.getElementsByTagName("Relationship")[0].attributes['Target'].value
    xmldoc = minidom.parse(z.open(pkgtarget[1:]))


    xml_streamid = streamid
    xml_Id = xmldoc.getElementsByTagName("id")[0].firstChild.data
    xml_Version = xmldoc.getElementsByTagName("version")[0].firstChild.data
    if xmldoc.getElementsByTagName("requireLicenseAcceptance")[0].firstChild.data.lower() == "false":
        xml_RequireLicenseAcceptance = False
    else:
        xml_RequireLicenseAcceptance = True
    xml_VersionDownloadCount = 0
    xml_DownloadCount = 0
    xml_IsLatestVersion = True
    xml_IsAbsoluteLatestVersion = True
    xml_IsPrerelease = False
    xml_Created = datetime.datetime.now()
    xml_LastUpdated = datetime.datetime.now()
    xml_Published = datetime.datetime.now()

    xml_PackageHash = hsha256.hexdigest()
    xml_PackageHashAlgorithm = "SHA256"
    xml_PackageSize = fsize

    xml_Copyright = ""
    xml_Dependencies = ""
    xml_GalleryDetailsUrl = ""
    xml_IconUrl = ""
    xml_Language = "en"
    xml_LicenseUrl =""
    xml_ReportAbuseUrl = ""
    xml_ReleaseNotes = ""

    tag = xmldoc.getElementsByTagName("title")
    if len (tag) == 0 or len(tag[0].childNodes) == 0:
        xml_Title = ""
    else: xml_Title = tag[0].firstChild.data
    tag = xmldoc.getElementsByTagName("authors")
    if len (tag) == 0 or len(tag[0].childNodes) == 0:
        xml_Authors = ""
    else: xml_Authors = tag[0].firstChild.data
    tag = xmldoc.getElementsByTagName("projectUrl")
    if len (tag) == 0 or len(tag[0].childNodes) == 0:
        xml_ProjectUrl = ""
    else: xml_ProjectUrl = tag[0].firstChild.data
    tag = xmldoc.getElementsByTagName("description")
    if len (tag) == 0 or len(tag[0].childNodes) == 0:
        xml_Description = ""
    else: xml_Description = tag[0].firstChild.data
    tag = xmldoc.getElementsByTagName("summary")
    if len (tag) == 0 or len(tag[0].childNodes) == 0:
        xml_Summary = ""
    else: xml_Summary = tag[0].firstChild.data
    tag = xmldoc.getElementsByTagName("tags")
    if len (tag) == 0 or len(tag[0].childNodes) == 0:
        xml_Tags = ""
    else: xml_Tags = tag[0].firstChild.data

db = sqlite3.connect('dbrepo.db')
with db:
    # CREATE TABLE "Packages" ("Id" TEXT NOT NULL, "Version" TEXT NOT NULL, "Authors" TEXT, "Copyright" TEXT, "Created" TIMESTAMP NOT NULL, "Dependencies" TEXT, "Description" TEXT, "DownloadCount" INTEGER NOT NULL, "GalleryDetailsUrl" TEXT, "IconUrl" TEXT, "IsLatestVersion" BOOLEAN NOT NULL, "IsAbsoluteLatestVersion" BOOLEAN NOT NULL, "IsPrerelease" BOOLEAN NOT NULL, "Language" TEXT, "LastUpdated" TIMESTAMP NOT NULL, "Published" TIMESTAMP NOT NULL, "LicenseUrl" TEXT, "PackageHash" TEXT, "PackageHashAlgorithm" TEXT, "PackageSize" INTEGER NOT NULL, "ProjectUrl" TEXT, "ReportAbuseUrl" TEXT, "ReleaseNotes" TEXT, "RequireLicenseAcceptance" BOOLEAN NOT NULL, "Summary" TEXT, "Tags" TEXT, "Title" TEXT, "VersionDownloadCount" INTEGER NOT NULL, "_value" INTEGER, PRIMARY KEY ("Version", "Id"));
    db.execute('INSERT INTO Packages VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', [xml_Id, xml_Version, xml_Authors, xml_Copyright, xml_Created, xml_Dependencies, xml_Description, xml_DownloadCount, xml_GalleryDetailsUrl, xml_IconUrl, xml_IsLatestVersion, xml_IsAbsoluteLatestVersion, xml_IsPrerelease, xml_Language, xml_LastUpdated, xml_Published, xml_LicenseUrl, xml_PackageHash, xml_PackageHashAlgorithm, xml_PackageSize, xml_ProjectUrl, xml_ReportAbuseUrl, xml_ReleaseNotes, xml_RequireLicenseAcceptance, xml_Summary, xml_Tags, xml_Title, xml_VersionDownloadCount, xml_streamid])
    db.commit()

