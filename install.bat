@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
cd /d "%ROOT%"
set "REQ=requirements.txt"

echo =====================================================
echo  ComfyUI Polaris - dependency installer
echo =====================================================
echo.

if not exist "%REQ%" (
    echo ERROR: %REQ% not found next to install.bat.
    exit /b 1
)

rem ---- pick a Python 3.8-3.12 interpreter ----
set "PYEXE="
where py >nul 2>nul
if not errorlevel 1 (
    py -3.12 -c "pass" >nul 2>nul
    if not errorlevel 1 set "PYEXE=py -3.12"
)
if not defined PYEXE (
    python -c "import sys; sys.exit(0 if (3, 8) <= sys.version_info[0:2] < (3, 13) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYEXE=python"
)
if not defined PYEXE (
    echo ERROR: Python 3.8-3.12 not found.
    echo Install Python 3.12 from https://www.python.org/downloads/ and re-run.
    exit /b 1
)
echo Using interpreter: %PYEXE%
echo.

echo [0/4] Folder structure
rem ---- runtime folders (a fresh clone ships none) ----
for %%D in (input output user temp custom_nodes blueprints) do if not exist "%%D" mkdir "%%D"
for %%D in (audio_encoders background_removal checkpoints clip clip_vision configs controlnet detection diffusers diffusion_models embeddings frame_interpolation geometry_estimation gligen hypernetworks latent_upscale_models loras model_patches optical_flow photomaker style_models text_encoders unet upscale_models vae vae_approx) do if not exist "models\%%D" mkdir "models\%%D"
rem ---- placeholder files (keep the folders visible in the UI) ----
for %%F in (
    "blueprints\put_blueprints_here"
    "models\audio_encoders\put_audio_encoder_models_here"
    "models\background_removal\put_background_removal_models_here"
    "models\checkpoints\put_checkpoints_here"
    "models\clip\put_clip_or_text_encoder_models_here"
    "models\clip_vision\put_clip_vision_models_here"
    "models\controlnet\put_controlnets_and_t2i_here"
    "models\detection\put_detection_models_here"
    "models\diffusers\put_diffusers_models_here"
    "models\diffusion_models\put_diffusion_model_files_here"
    "models\embeddings\put_embeddings_or_textual_inversion_concepts_here"
    "models\frame_interpolation\put_frame_interpolation_models_here"
    "models\geometry_estimation\put_geometry_estimation_models_here"
    "models\gligen\put_gligen_models_here"
    "models\hypernetworks\put_hypernetworks_here"
    "models\latent_upscale_models\put_latent_upscale_models_here"
    "models\loras\put_loras_here"
    "models\model_patches\put_model_patches_here"
    "models\optical_flow\put_optical_flow_models_here"
    "models\photomaker\put_photomaker_models_here"
    "models\style_models\put_t2i_style_model_here"
    "models\text_encoders\put_text_encoder_files_here"
    "models\unet\put_unet_files_here"
    "models\upscale_models\put_esrgan_and_other_upscale_models_here"
    "models\vae\put_vae_here"
    "models\vae_approx\put_taesd_encoder_pth_and_taesd_decoder_pth_here"
    "output\_output_images_will_be_put_here"
) do if not exist "%%~F" type nul > "%%~F"
echo.

echo [1/4] DirectML venv (.venv) - primary Polaris backend
if not exist ".venv\Scripts\python.exe" (
    %PYEXE% -m venv .venv
    if errorlevel 1 ( echo ERROR: failed to create .venv & exit /b 1 )
)
call :extract DIRECTML "%TEMP%\req-directml.txt"
if errorlevel 1 ( echo ERROR: DIRECTML section missing in %REQ% & exit /b 1 )
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
".venv\Scripts\python.exe" -m pip install -r "%TEMP%\req-directml.txt"
if errorlevel 1 ( echo ERROR: DirectML dependencies failed to install. & exit /b 1 )
echo.

echo [2/4] ComfyUI-Manager (.venv)
call :extract MANAGER "%TEMP%\req-manager.txt"
if not errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r "%TEMP%\req-manager.txt"
)
echo.

echo [3/4] ZLUDA venv (.venv-zluda) - optional backend
if not exist ".venv-zluda\Scripts\python.exe" (
    %PYEXE% -m venv .venv-zluda
    if errorlevel 1 ( echo ERROR: failed to create .venv-zluda & exit /b 1 )
)
call :extract ZLUDA "%TEMP%\req-zluda.txt"
if errorlevel 1 ( echo ERROR: ZLUDA section missing in %REQ% & exit /b 1 )
".venv-zluda\Scripts\python.exe" -m pip install --upgrade pip >nul
".venv-zluda\Scripts\python.exe" -m pip install -r "%TEMP%\req-zluda.txt"
if errorlevel 1 ( echo ERROR: ZLUDA dependencies failed to install. & exit /b 1 )
echo.

echo [4/4] ZLUDA runtime download + deploy
set "DL=%TEMP%\comfyui-polaris"
if not exist "%DL%" mkdir "%DL%"
set "ZL_ZIP=%DL%\zluda.zip"
set "ALUP_7Z=%DL%\alup-gfx803.7z"
set "SZR=%DL%\7zr.exe"

rem ---- ZLUDA CUDA shims (windows-rocm5, from lshqqytiger/ZLUDA releases) ----
if not exist "%ZL_ZIP%" (
    curl.exe --ssl-no-revoke -sL -o "%ZL_ZIP%" "https://github.com/lshqqytiger/ZLUDA/releases/download/rel.5e717459179dc272b7d7d23391f0fad66c7459cf/ZLUDA-windows-rocm5-amd64.zip" >nul 2>nul
)
if not exist "%ZL_ZIP%" (
    echo     WARNING: ZLUDA download failed - shims NOT deployed.
) else (
    if exist ".venv-zluda\Lib\site-packages\torch\lib" (
        if not exist "%DL%\zluda\nvcuda.dll" (
            tar -xf "%ZL_ZIP%" -C "%DL%" >nul 2>nul
        )
        if exist "%DL%\zluda\nvcuda.dll" (
            copy /y "%DL%\zluda\nvcuda.dll"   ".venv-zluda\Lib\site-packages\torch\lib\nvcuda.dll"     >nul
            copy /y "%DL%\zluda\cublas.dll"   ".venv-zluda\Lib\site-packages\torch\lib\cublas64_11.dll" >nul
            copy /y "%DL%\zluda\cusparse.dll" ".venv-zluda\Lib\site-packages\torch\lib\cusparse64_11.dll" >nul
            copy /y "%DL%\zluda\nvrtc.dll"    ".venv-zluda\Lib\site-packages\torch\lib\nvrtc64_112_0.dll" >nul
            echo     ZLUDA shims deployed to .venv-zluda\torch\lib
        ) else (
            echo     WARNING: ZLUDA extract failed - shims NOT deployed.
        )
    ) else (
        echo     WARNING: .venv-zluda\torch\lib not found - ZLUDA shims NOT deployed.
    )
)

rem ---- gfx803 rocBLAS pack (from advanced-lvl-up releases) ----
if defined HIP_PATH (
    if not exist "%ALUP_7Z%" (
        curl.exe --ssl-no-revoke -sL -o "%ALUP_7Z%" "https://github.com/advanced-lvl-up/Rx470-Vega10-Rx580-gfx803-gfx900-fix-AMD-GPU/releases/download/v1.0.0/rocm.gfx800-gfx900-for.hip.sdk.5.7.1-and-6.2.4.7z" >nul 2>nul
    )
    if not exist "%SZR%" (
        curl.exe --ssl-no-revoke -sL -o "%SZR%" "https://www.7-zip.org/a/7zr.exe" >nul 2>nul
    )
    if not exist "%ALUP_7Z%" (
        echo     WARNING: gfx803 rocBLAS pack download failed - NOT deployed.
    ) else if not exist "%SZR%" (
        echo     WARNING: 7zr.exe download failed - gfx803 rocBLAS pack NOT deployed.
    ) else (
        if not exist "%DL%\rocm-alup\rocblas.dll" (
            "%SZR%" x "%ALUP_7Z%" "-o%DL%\rocm-alup" -y >nul 2>nul
        )
        if exist "%DL%\rocm-alup\rocblas.dll" (
            if not exist "%HIP_PATH%\bin" mkdir "%HIP_PATH%\bin"
            copy /y "%DL%\rocm-alup\rocblas.dll" "%HIP_PATH%\bin\rocblas.dll" >nul
            if not exist "%HIP_PATH%\bin\library" mkdir "%HIP_PATH%\bin\library"
            xcopy /e /y /q "%DL%\rocm-alup\library" "%HIP_PATH%\bin\library\" >nul
            echo     gfx803 rocBLAS pack deployed to %HIP_PATH%\bin
        ) else (
            echo     WARNING: gfx803 rocBLAS pack extract failed - NOT deployed.
        )
    )
) else (
    echo     WARNING: HIP_PATH not set - gfx803 rocBLAS pack NOT deployed.
    echo     Install the HIP SDK and set HIP_PATH, then re-run install.bat.
)
echo.

echo =====================================================
echo  Done. Run ComfyUI:
echo    .venv\Scripts\python.exe main.py --directml 0 --cpu-vae
echo    python main.py --zluda    (relaunches into .venv-zluda)
echo =====================================================
exit /b 0

rem -------------------------------------------------------
rem  Extract the dependency lines of one marked section from
rem  requirements.txt into %2. Sections are delimited by
rem  lines matching:  # ==== SECTIONNAME ====
rem -------------------------------------------------------
:extract
set "SEC=%~1"
set "OUT=%~2"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$lines = Get-Content -LiteralPath 'requirements.txt' -Encoding UTF8; $on = $false; $out = @(); foreach ($s in $lines) { if ($s -match '^# ==== ') { $on = ($s -match '^# ==== %SEC% ====$'); continue }; if ($on -and $s -match '\S' -and $s -notmatch '^# *=+ *$') { $out += $s } }; if ($out.Count -eq 0) { exit 1 }; Set-Content -LiteralPath '%OUT%' -Value $out -Encoding UTF8"
exit /b %errorlevel%
