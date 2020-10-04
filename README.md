# Back-Shelter
This is a Prototype of a realtime Backup-Script.
The Script is splitted into main parts.

The first part is the server-script which open up a few ports to communicate with the clients which are mostly also other Server.
The server has two folders and a list. The two folders are seperated into "cache" and "storage".
If any client uploads a file, it will be saved into the cache-folder. Then checks the Server if this file exsits in a newer version and log it into a log-file.
Then puts the server the file into the storage-folder and edit a list where every file is append and where also the last edeting-date of the file is noted.
The clients download this list and check if the have older or newer files.
If the file is newer, they upload it to the cache-folder.
If the file is older, they download the file from the storage-folder.
But they check only each file in the client-storage-folder which is on every client located, because else they would backup systeminformations or other privat data.
If then the server or a client crashs and can't be recovert. You can easely configer the system and the Back-Shelter and everything is fine.

This program is a open-source version of epic-shelter which is used by the NSA. This is ONLY for Linux.

