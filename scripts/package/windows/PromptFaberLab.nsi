!define APP_NAME "Prompt Faber Lab"
!define APP_EXE_NAME "PromptFaberLab.exe"
!define COMPANY_NAME "Prompt Faber"
!define REG_ROOT "HKLM"
!define REG_KEY "Software\${COMPANY_NAME}\${APP_NAME}"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

!ifndef PFL_VERSION
  !define PFL_VERSION "0.1.0"
!endif

OutFile "$%PFL_OUTDIR\PromptFaberLab-${PFL_VERSION}-setup.exe"
InstallDir "$PROGRAMFILES64\PromptFaberLab"
RequestExecutionLevel admin

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  File /oname=${APP_EXE_NAME} "$%PFL_EXE"

  WriteRegStr ${REG_ROOT} "${REG_KEY}" "InstallDir" "$INSTDIR"
  WriteRegStr ${REG_ROOT} "${UNINST_KEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr ${REG_ROOT} "${UNINST_KEY}" "DisplayVersion" "${PFL_VERSION}"
  WriteRegStr ${REG_ROOT} "${UNINST_KEY}" "Publisher" "${COMPANY_NAME}"
  WriteRegStr ${REG_ROOT} "${UNINST_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr ${REG_ROOT} "${UNINST_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE_NAME}"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$INSTDIR\${APP_EXE_NAME}"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  DeleteRegKey ${REG_ROOT} "${REG_KEY}"
  DeleteRegKey ${REG_ROOT} "${UNINST_KEY}"
SectionEnd
