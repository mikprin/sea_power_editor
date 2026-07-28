@echo off
set "SOURCE=.\campaigns\PhantomWake"
set "DEST=E:\STEAM\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets\user\campaigns\PhantomWake"

echo Copying campaign files...
xcopy "%SOURCE%" "%DEST%" /E /I /H /Y

if %ERRORLEVEL% equ 0 (
    echo Copy completed successfully!
) else (
    echo An error occurred during copying.
)

pause