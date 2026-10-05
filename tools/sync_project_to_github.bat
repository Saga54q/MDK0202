@echo off
chcp 65001 > nul
rem =====================================================================
rem  sync_project_to_github.bat
rem  Переносит текущее состояние проекта lab1_quote_generator из рабочего
rem  репозитория MDK0202 в отдельный репозиторий проекта на GitHub.
rem
rem  Как пользоваться:
rem   1. Один раз отредактируй пути SOURCE и DEST ниже (см. комментарии).
rem   2. Дважды кликни по файлу или запусти его из терминала.
rem
rem  Что делает: копирует файлы проекта (кроме служебных), обновляет
rem  .gitignore и .gitattributes, затем коммитит и отправляет на GitHub.
rem =====================================================================
setlocal

rem --- Папка проекта в рабочем репозитории (источник) -----------------
set "SOURCE=C:\Projects\MDK0202\lab1_quote_generator"

rem --- Папка клона отдельного репозитория проекта (приёмник) ----------
rem Её нужно получить один раз командой:
rem   git clone https://github.com/Saga54q/lab1_quote_generator.git "C:\Projects\lab1_quote_generator"
set "DEST=C:\Projects\lab1_quote_generator"

rem =====================================================================

if not exist "%SOURCE%\src\main.py" (
    echo [ОШИБКА] Не найдена папка источника: %SOURCE%
    echo Проверь переменную SOURCE в начале этого файла.
    goto :fail
)

if not exist "%DEST%\.git" (
    echo [ОШИБКА] Не найден git-репозиторий проекта: %DEST%
    echo Сначала выполни:
    echo   git clone https://github.com/Saga54q/lab1_quote_generator.git "%DEST%"
    goto :fail
)

echo.
echo [1/3] Копирование файлов проекта...
rem /E  — копировать новые и изменённые файлы (ничего не удаляя)
rem /XD — исключить служебные каталоги, в том числе .git приёмника
rem /XF — исключить кэш байт-кода
robocopy "%SOURCE%" "%DEST%" /E /XD .git .idea .vscode __pycache__ /XF *.pyc *.py.class > nul
if errorlevel 8 goto :rc_error

echo [2/3] Обновление .gitignore и .gitattributes...
copy /Y "%~dp0..\.gitignore"     "%DEST%\.gitignore" > nul
copy /Y "%~dp0..\.gitattributes" "%DEST%\.gitattributes" > nul

echo [3/3] Коммит и отправка на GitHub...
pushd "%DEST%"
git add .
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "sync: изменения из MDK0202"
    git push
    if errorlevel 1 (
        echo.
        echo [ВНИМАНИЕ] Отправка не удалась. Если ветка ещё не привязана, выполни
        echo   git push -u origin main
        popd
        goto :fail
    )
) else (
    echo Изменений нет — коммит не нужен.
)
popd

echo.
echo Готово: изменения перенесены и отправлены.
echo Примечание: удалённые в MDK0202 файлы в приёмнике остаются.
echo Для полной синхронизации замени /E на /MIR в строке robocopy.
endlocal
exit /b 0

:rc_error
echo.
echo [ОШИБКА] robocopy завершился с кодом %errorlevel% ^(ошибка при копировании^).
goto :fail

:fail
endlocal
exit /b 1
