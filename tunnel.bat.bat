@echo off
echo ============================================
echo   Туннель Serveo запущен
echo   Скопируйте URL из строки ниже:
echo ============================================
ssh -R 80:localhost:5000 serveo.net
pause