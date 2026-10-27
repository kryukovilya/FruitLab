import Varwin
from SceneObjectTypes import *

defaultSpawnPoint = DefaultSpawnPointWrapper(Varwin.Objects.GetObjectByVarName("defaultSpawnPoint"))
player = PlayerWrapper(Varwin.Objects.GetObjectByVarName("player"))
spaceEnv = SpaceEnvWrapper(Varwin.Objects.GetObjectByVarName("spaceEnv"))
pointLight = VPointLightWrapper(Varwin.Objects.GetObjectByVarName("pointLight"))
text = VTextWrapper(Varwin.Objects.GetObjectByVarName("text"))
text2 = VTextWrapper(Varwin.Objects.GetObjectByVarName("text2"))
text3 = VTextWrapper(Varwin.Objects.GetObjectByVarName("text3"))
classic = CustomZoneWrapper(Varwin.Objects.GetObjectByVarName("classic"))
hard = CustomZoneWrapper(Varwin.Objects.GetObjectByVarName("hard"))
cube = VCubeWrapper(Varwin.Objects.GetObjectByVarName("cube"))
cube2 = VCubeWrapper(Varwin.Objects.GetObjectByVarName("cube2"))
spaceCircle = SpaceCircleWrapper(Varwin.Objects.GetObjectByVarName("spaceCircle"))
directionalLight = VDirectionalLightWrapper(Varwin.Objects.GetObjectByVarName("directionalLight"))
lamp = VarwinAudioWrapper(Varwin.Objects.GetObjectByVarName("lamp"))
engine = VarwinAudioWrapper(Varwin.Objects.GetObjectByVarName("engine"))
