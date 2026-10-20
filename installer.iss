[Setup]
AppName=bhaner
AppVersion=1.3.0
DefaultDirName={autopf}\bhaner
DefaultGroupName=bhaner
UninstallDisplayIcon={app}\bhaner.exe
Compression=lzma2
SolidCompression=yes
OutputDir=dist_installer
OutputBaseFilename=bhaner_Setup_v1.3.0

[Files]
Source: "dist\bhaner.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "THEMES_GUIDE.md"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{autoprograms}\bhaner"; Filename: "{app}\bhaner.exe"
Name: "{autodesktop}\bhaner"; Filename: "{app}\bhaner.exe"

[Run]
Filename: "{app}\bhaner.exe"; Description: "Launch bhaner Stage Controller"; Flags: postinstall nowait skipifsilent