<h1 align="center">Hi there, I'm ITgenerat0r.</h1>
This script tracks your file. When the key text appears there, he will send this string to the recipients using a Telegram bot. (It can be adapted to any event.)


You can set the keys in the file keys.txt. Use an space or end line as a separator.

Before you start, you should create your own Telegram bot and get a token. Start the server.py or a single.py file, then go to the bot and get your username and password there (command: /start).

There are two configurations:

**1. Split**

You run a stable server 24/7 and run a client on your computer where you need to monitor any event.
The server receives data from the client and sends it using a Telegram bot. The server also checks if the client has lost the connection.

Run server:
```terminal
python full_server.py -port "IP_PORT_FOR_LISTENING" -token <YOUR_TELEGRAM_BOT_TOKEN> -dbhost <DATABASE_IP (recommend: 127.0.0.1)> -dbuser <DATABASE_USERLOGIN> -dbpass <DATABASE_USERPASSWORD> -dbname <YOUR_DATABASE_NAME> -admins <id admins(splitter: space)>
```


Run client:
```terminal
<a>python client.py -u <LOGIN> -name <NAME(who sended data, or some key text)> -f <INPUT_FILE> -ip <SERVER_IP> -port <SERVER_PORT></a>
```


**2. Single**

You run a single file on your computer in which you need to track any event. It's simple, but you can't see if your computer is turned off.

Run single:
```terminal
	python alarm.py -token <YOUR_TELEGRAM_BOT_TOKEN> -u <RECEIVER_LOGIN_1> <RECEIVER_LOGIN_2> <...>
```
Additional options:
```terminal
  -name <NAME(who sended data, or some key text)> -f <INPUT_FILE> -d <DELAY (delay between checks file data, in seconds)>
```

You can also compile the files to single.exe and run it on a clean OS.
