

from PySide2 import QtWidgets


# usdPath = "/home/vrman/Documents/Asset/modelling/Asset.Source.usd"

# usdStage = Usd.Stage.Open(usdPath)
# usdPrim = usdStage.GetPrimAtPath("/Cube/CubeShape")



# primvarsSchema = UsdGeom.PrimvarsAPI(usdPrim)
# primvar = primvarsSchema.CreatePrimvar(
#      "ri:attributes:displacementbound:sphere",
#      Sdf.ValueTypeNames.Float,
#      interpolation=UsdGeom.Tokens.constant )

# primvar.Set(0.1)




# usdStage.GetRootLayer().Save()





def main ():

    class FileDialog (QtWidgets.QFileDialog):

          def __init__ (self):
              super(FileDialog, self).__init__()

    widget = FileDialog()
    path = widget.getExistingDirectory()

    print( type(path), path )
