import Varwin
from SceneObjects import *

leve = Varwin.Variable()
Score2 = Varwin.Variable()

# Описание функции
async def setText():
  Score.SetText('0')
  await Varwin.WaitForSeconds(0.8)
  ost.SetText('0')

async def OnPrepareSceneChain1():
  leve.Value = 0
  Score2.Value = 0
  player.PointerLength = 0

async def OnWin1(sender):
  leve.Value = leve.Value + 1
  ost.SetText(leve.Value)
  await audio.PlaySound()
  if leve.Value == 1:
    await audio5.PlaySound()
  if leve.Value == 2:
    await audio7.PlaySound()
  if leve.Value == 3:
    await audio6.PlaySound()
  exporpriationCamera.Refresh()

async def OnOnDrop1(sender):
  await audio8.PlaySound()

async def OnPlaybackCompleted1(sender):
  exporpriationCamera.Refresh()
  player.PointerLength = 5000

async def OnPlaybackCompleted2(sender):
  await Varwin.WaitForSeconds(1)
  Varwin.Project.LoadSceneByGuid("dbfc37af-bd68-4f95-b1e0-05b7484db5b3")

async def OnPlaybackCompleted3(sender):
  await audio4.PlaySound()

async def OnLose1(sender):
  player.PointerLength = 0
  sphere.Activity = True;
  sphere2.Red()
  text.SetText('УВОЛЕН')
  text2.SetText('УВОЛЕН')
  text3.SetText('УВОЛЕН')
  await Allert.PlaySound()

async def OnDestroy1(sender):
  Score2.Value = Score2.Value + 1
  await audio9.PlaySound()
  Score.SetText(Score2.Value)

async def Chain5():
  sphere2.Open()
  await audio3.PlaySound()
  await setText()
  await audio2.PlaySound()

Varwin.Project.AddPrepareSceneHandler(OnPrepareSceneChain1)

exporpriationCamera.AddWinHandler(OnWin1)
for instance in Varwin.Objects.GetObjectsOfType(FruitlabCubeWrapper):
  instance.AddOnDropHandler(OnOnDrop1)

audio2.AddPlaybackCompletedHandler(OnPlaybackCompleted1)
exporpriationCamera.AddLoseHandler(OnLose1)
for instance in Varwin.Objects.GetObjectsOfType(FruitlabCubeWrapper):
  instance.AddDestroyHandler(OnDestroy1)

audio4.AddPlaybackCompletedHandler(OnPlaybackCompleted2)
Allert.AddPlaybackCompletedHandler(OnPlaybackCompleted3)

Varwin.Async.Run(Chain5())
