#define MyAppName "PDIE"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "ProAssist"
#define MyAppExeName "pdie.exe"

[Setup]
AppId={{B8B5C2A3-0D02-40D5-A7A9-8FD7B4D5D773}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist\installer
OutputBaseFilename=setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesEnvironment=yes

[Files]
Source: "..\dist\pdie\pdie.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PDIE Command Prompt"; Filename: "{cmd}"; Parameters: "/K ""cd /d {app} && pdie --help"""; WorkingDir: "{app}"
Name: "{group}\Uninstall PDIE"; Filename: "{uninstallexe}"

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}"; Check: NeedsAddPath(ExpandConstant('{app}'))

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Uppercase(Param) + ';', ';' + Uppercase(OrigPath) + ';') = 0;
end;
