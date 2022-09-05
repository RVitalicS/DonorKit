Create ASSETLIBS environment variable that contain directories that would be read as libraries. If it doesn't set `<root>/examples/library` will be used by default
<br/><br/>
That directory has hidden *.metadata.json* file to interpret structure of folders as Assets Library
```json
{
    "info": "",
    "name": "Library",
    "type": "root"
}
```