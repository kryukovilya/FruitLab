import Varwin
from SceneObjects import *

async def OnObjectEntered1(zoneTarget, sender):
  Varwin.Project.LoadSceneByGuid("e1749af5-38f7-4bc9-bc1d-ee1a99e88280")

async def OnObjectEntered2(zoneTarget, sender):
  Varwin.Project.LoadSceneByGuid("cab68c39-caff-47ff-a89f-6568ddd50a29")

async def Chain1():
  spaceEnv.Intro()
  await lamp.PlaySound()
  await engine.PlaySound()
  pointLight.Intensity = 1

hard.AddObjectEnteredHandler(OnObjectEntered1)
classic.AddObjectEnteredHandler(OnObjectEntered2)

Varwin.Async.Run(Chain1())
