Chocorepo
=========

Trying to mimic NuGet repository.

Goal
----

Being able to serve Nuget packages from any machine that can run Python without having to install Visual Studio and Nuget.server.

Usage
-----

On your Linux box (e.g. 192.168.150.19) :

1- python repo.py
(creates the db files)

2- python import ../pkg/notepadplusplus.nupkg
(imports Notepad++ package into the database)

3- python repo.py
(starts Chocorepo)

On your Windows box :

1- chocolatey list -source http://192.168.150.19:8080/
(list all packages from your Linux box)

2- chocolatey install notepadplusplus -source http://192.168.150.19:8080/
(install package Notepad++)

In repo.py, some variables might be change :
- SERVICE_PORT = port to bind to
- SERVICE_ROOT = the name of the server (important because it is returned in html response)
- SERVE_ADDRESS = address to bind to

Credits
-------

Using Pyslet http://www.pyslet.org/ (Thank you Steve!)

metadata file comes from : http://chocolatey.org/api/v2/$metadata
