cd /home/gen/tg_alarm
screen -dmS alarm_bot python3 main.py -prod
screen -dmS alarm_serv python3 server.py -log