import Varwin
from SceneObjects import *

Time = Varwin.Variable()
loose = Varwin.Variable()
Score = Varwin.Variable()
Pause = Varwin.Variable()
level2 = Varwin.Variable()

# Описание функции
async def setupScreens():
  score.SetText('0')
  await Varwin.WaitForSeconds(1)
  level.SetText('0')

# Описание функции
async def startTimer():
  while Time.Value > 0 or loose.Value == 1:
    while (Pause.Value == 1):
      await Varwin.WaitForEndOfFrame()
    await Varwin.WaitForSeconds(1)
    Time.Value = Time.Value + -1
    timer1.SetText(Time.Value)
    timer2.SetText(Time.Value)
  Time.Value = 0
  await lose()

# Describe this function...
async def lose():
  await allert.PlaySound()
  await outro.PlaySound()
  sphere4.Activity = True;
  Pause.Value = 1
  player.PointerLength = 0
  simpleButton.InteractionBehaviour.CanUse = Varwin.InteractionBehaviour.UseState.Disabled
  casino.Off()
  sphere.Red()
  await Varwin.WaitForSeconds(3)
  Varwin.Project.LoadSceneByGuid("dbfc37af-bd68-4f95-b1e0-05b7484db5b3")

async def OnPrepareSceneChain1():
  player.PointerLength = 0
  Time.Value = 15
  loose.Value = 0
  Pause.Value = 0
  Score.Value = 0
  level2.Value = 0

async def OnPressed1(sender):
  simpleButton.InteractionBehaviour.CanUse = Varwin.InteractionBehaviour.UseState.Disabled
  casino.StartSpin()
  await roll.PlaySound()

async def OnOnDrop1(sender):
  await drop.PlaySound()

async def OnWin1(sender):
  timer1.SetText(Time.Value)
  timer2.SetText(Time.Value)
  exporpriationCamera.Refresh()
  casino.On()
  Time.Value = Time.Value + 5
  level2.Value = level2.Value + 1
  level.SetText(level2.Value)
  simpleButton.SetReleasedState()
  simpleButton.InteractionBehaviour.CanUse = Varwin.InteractionBehaviour.UseState.Enabled

async def OnPlaybackCompleted1(sender):
  await allert.PlaySound()
  player.PointerLength = 5000
  exporpriationCamera.Refresh()
  casino.On()
  await startTimer()

async def OnPlaybackCompleted2(sender):
  casino.win()
  await gampl.PlaySound()
  await Varwin.WaitForSeconds(1)
  casino.Off()

async def OnLose1(sender):
  await lose()

async def OnDestroy1(sender):
  if not Pause.Value == 1:
    await destroy.PlaySound()
    Score.Value = Score.Value + 1
    score.SetText(Score.Value)
    Time.Value = Time.Value + 2
    timer1.SetText(Time.Value)
    timer2.SetText(Time.Value)

async def Chain4():
  sphere.Open()
  await setupScreens()
  await intro.PlaySound()

Varwin.Project.AddPrepareSceneHandler(OnPrepareSceneChain1)

simpleButton.AddPressedHandler(OnPressed1)
for instance in Varwin.Objects.GetObjectsOfType(FruitlabCubeWrapper):
  instance.AddOnDropHandler(OnOnDrop1)

exporpriationCamera.AddWinHandler(OnWin1)
intro.AddPlaybackCompletedHandler(OnPlaybackCompleted1)
roll.AddPlaybackCompletedHandler(OnPlaybackCompleted2)
for instance in Varwin.Objects.GetObjectsOfType(ExporpriationCameraWrapper):
  instance.AddLoseHandler(OnLose1)

for instance in Varwin.Objects.GetObjectsOfType(FruitlabCubeWrapper):
  instance.AddDestroyHandler(OnDestroy1)

Varwin.Async.Run(Chain4())
