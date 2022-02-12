
#### AssetName

+ **previews**
        *AssetName.v01.png*

+ **modelling**
        *ModelName.v01.Proxy.usdc*
        *ModelName.v01.usdc*

+ **animation**
        *AnimationName.v01.usdc*

+ **surfacing**
        *SurfaceName.v01.RenderMan.usda*
        *SurfaceName.v01.usda*

    AssetName.v01.AnimationName.usda
    AssetName.Final.AnimationName.usda (symlink)



File with *.Final.* tag is symbolic link that would be updated to a last exported version (by default)
```bash
AssetName.v01.usda
AssetName.v02.usda
AssetName.v03.usda
AssetName.Final.usda -> AssetName.v03.usda
```



Root folder (**AssetName**) has hidden *.metadata.json* file to interpret structure of 
refereced layers and folder groups as Usd Asset

```json
{
    "info": "",
    "published": "00.00.0000 00.00",
    "type": "usdasset",
    "status": "WIP"
}
```



File names are combinations of dot separated components

| name      | version or status tag, variant | reserved tag or animation name | extension |
| --------- | ------------------------------ | ------------------------------ | --------- |
| AssetName | Final                          | AnimationName                  | usd       |
|           | v01                            | Proxy                          | png       |
|           | v01-VariantName                | RenderMan                      |           |
