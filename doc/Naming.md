#### Naming
File names are combinations of dot separated components

| name      | version or status tag, variant | reserved tag or animation name | extension |
|-----------|--------------------------------|--------------------------------|-----------|
| AssetName | Final                          | AnimationName                  | usd       |
|           | v01                            | Proxy                          | png       |
|           | v01-VariantName                | RenderMan                      |           |

<br/><br/>
#### Hierarchy
```bash
# AssetName

[previews]
    [AssetName.v01.AnimationName]
        Hydra.f001.png
        ...
        Hydra.f120.png
        Prman.f001.png

[modelling]
    ModelName.v01.usdc
    ModelName.v01.Proxy.usdc

[animation]
    AnimationName.v01.usdc

[surfacing]
    [SurfaceName]
        [textures]
        v01.usda
        v01.RenderMan.usda
        v01.Hydra.usda

[surfacing]
    AssetName.v01.AnimationName.mb

AssetName.v01.AnimationName.usda
AssetName.Final.AnimationName.usda (symlink)
```

<br/><br/>
File with *.Final.* tag is symbolic link that would be updated to a last exported version (by default)
```bash
AssetName.v01.usda
AssetName.v02.usda
AssetName.v03.usda
AssetName.Final.usda -> AssetName.v03.usda
```
