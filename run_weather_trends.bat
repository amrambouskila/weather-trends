@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM              CONFIGURATION (EDIT THESE ONLY)
REM ============================================================
set "COMPOSE_FILE=docker-compose.yml"
set "PROJECT_PREFIX=weather-trends"

REM ============================================================
REM                     START THE SERVICE
REM ============================================================
call :start_service

:show_menu
echo.
echo ==============================
echo Weather Trends Analyzer
echo.
echo   k = stop (keep image)
echo   q = stop + remove image
echo   v = stop + remove image + volumes
echo   r = full restart (stop, remove, rebuild, relaunch)
echo ==============================

REM ============================================================
REM                     MAIN LOOP
REM ============================================================
:main_loop
set /p "CHOICE=Enter selection (k/q/v/r): "
if /I "%CHOICE%"=="k" goto do_stop
if /I "%CHOICE%"=="q" goto do_cleanup
if /I "%CHOICE%"=="v" goto do_cleanup_volumes
if /I "%CHOICE%"=="r" goto do_restart
echo Invalid selection. Enter k, q, v, or r.
goto main_loop

REM ============================================================
REM            k = STOP BUT KEEP IMAGE
REM ============================================================
:do_stop
echo.
echo Stopping containers...
docker compose -f "%COMPOSE_FILE%" down
echo Done.
goto end_script

REM ============================================================
REM            q = STOP + REMOVE IMAGE
REM ============================================================
:do_cleanup
echo.
echo Stopping containers...
docker compose -f "%COMPOSE_FILE%" down --remove-orphans
call :remove_images
echo Done.
goto end_script

REM ============================================================
REM            v = STOP + REMOVE IMAGE + VOLUMES
REM ============================================================
:do_cleanup_volumes
echo.
echo Stopping containers and removing volumes...
docker compose -f "%COMPOSE_FILE%" down --volumes --remove-orphans
call :remove_images
echo Done.
goto end_script

REM ============================================================
REM            r = FULL RESTART
REM ============================================================
:do_restart
echo.
echo === FULL RESTART ===
echo Stopping containers...
docker compose -f "%COMPOSE_FILE%" down --remove-orphans
call :remove_images
echo.
call :start_service
goto show_menu

REM ============================================================
REM                    HELPER: START SERVICE
REM ============================================================
:start_service
echo.
echo ============================================
echo        WEATHER TRENDS ANALYZER
echo ============================================
echo.
echo Starting Docker Compose...
docker compose -f "%COMPOSE_FILE%" up --build -d

echo.
echo ============================================
echo   Service is running.
echo.
echo   Charts will be saved to: .\output\
echo ============================================
goto :eof

REM ============================================================
REM                    HELPER: REMOVE IMAGES
REM ============================================================
:remove_images
echo.
echo Removing images...

for /f "delims=" %%I in ('
    docker compose -f "%COMPOSE_FILE%" config --images 2^>nul
') do (
    echo Found image: %%I
    docker rmi -f "%%I" 2>nul
)

for /f "delims=" %%I in ('
    docker images --format "{{.Repository}}:{{.Tag}}" ^| findstr /I "%PROJECT_PREFIX%"
') do (
    echo Found image: %%I
    docker rmi -f "%%I" 2>nul
)

echo Images removed.
goto :eof

REM ============================================================
REM                            END
REM ============================================================
:end_script
pause
exit /B