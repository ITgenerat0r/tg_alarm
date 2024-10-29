Dim oShell 
Set oShell = WScript.CreateObject ("WSCript.shell") 
oShell.run "python d:\generat0r\server.py > log", 0 
Set oShell = Nothing