# SAVE-THIS-YT-STREAM
Python programm, that can be used for recording streams

*Версия - 1.0.1.1 beta*
- Теперь все сегменты собираются в блоки по 20 штук, из за чего количество файлов во временной папке будет гораздо меньше, однако потребление оперативной памяти было повышенно(в пике может быть до 100-200мб)
- Добавлена возможность экстренной остановки по CTRL+C
- Незначительные фиксы и изменения

------------

#### Установка и настройка
Для работы вам потребуется модуль `ffmpeg`. Для того чтобы установить его в
- Ubuntu/Debian, используйте команду
`sudo apt install ffmpeg`

- Для установки в Windows скачате [Билд от zeranoe](https://ffmpeg.zeranoe.com/builds/ "Билд от zeranoe") . Из папки **bin** скопируйте файл **ffmpeg.exe** в папку ***C:/Windows/System32/***

После чего установите модули, используя `pip`
`pip install m3u8`
`pip install streamlink`

Далее осталось запустить программу

- В Windows - 
	`python save-stream.py` 
- В Linux -
	`python3 save-stream.py` 

------------
E-Mail - ivan@ttdl.ru
VK - [@crush_bandicot](https://vk.com/crush_bandicot "@crush_bandicot")
Discord - Ivanisplaying#5024
