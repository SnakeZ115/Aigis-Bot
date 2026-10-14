Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Obtener la ruta del directorio del proyecto
ScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
ProjectDir = fso.GetParentFolderName(ScriptDir)

WshShell.CurrentDirectory = ProjectDir

' Preferir pythonw del entorno virtual si existe, sino el de Windows
VenvPython = ProjectDir & "\venv\Scripts\pythonw.exe"
If fso.FileExists(VenvPython) Then
    PythonExe = VenvPython
Else
    PythonExe = "pythonw.exe"
End If

' Ejecutar main.py en segundo plano (0 = ventana oculta, False = no esperar a que termine)
WshShell.Run """" & PythonExe & """ """ & ProjectDir & "\main.py""", 0, False
