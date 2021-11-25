____________________________________________________________________________________________________________________________________
OVERVIEW
____________________________________________________________________________________________________________________________________
This script pulls audio and closed caption data from YouTube. Depending on the podcast, there may be chapters (AKA tracks) for
different sections, these will be retained in output files. You can optionally break out the audio into chapters. A .vtt file containing
all chapters that contains time stamps for every closed caption is produced as well as more readable .subs files for each chapter without
time stamps. Both the .vtt and the .subs can be opened in a text editor like notepad++.
____________________________________________________________________________________________________________________________________
DEPENDENCIES
____________________________________________________________________________________________________________________________________
Other than supporting the modules that are imported, you must install youtube-dl (pip install) and ffmpeg if splitting audio into chapters
is desired (third argument when you call the script). Install the lgpl version of ffmpeg, move ffmpeg.exe into the same folder as the
podcast_downloader.py script (or anywhere in the python PATH).
____________________________________________________________________________________________________________________________________
USAGE
____________________________________________________________________________________________________________________________________
windows:

'***********************************************************************************************************************************************'
1. create folder where you want output files (subtitle text, audio tracks) to be (ex desktop\podcast_subs)

virtualenv method

2. place python script (podcast_downloader.py) in folder you created
3. open command prompt (windows key > "cmd" > enter)
4. create virtual environment

4 a. cd to folder created (ex. cd desktop\podcast_subs)

4 b. py-m venv env

4 c. .\env\Scripts\activate

5. install dependencies (click, youtube-dl, etc)
ex. pip install click
6. call file, pass arguments in; ex. below

python podcast_downloader.py "https://www.youtube.com/watch?v=bLDpJO795Os", "C:/Users/mizr3/Desktop/podcast_downloader", 'subs_only'

IDE & shell method

2. opens script in your IDE
3. install dependencies (click, youtube-dl, etc)
4. comment "click." lines and "if __name__" section
5. add line at end to call the main function

main("https://www.youtube.com/watch?v=bLDpJO795Os", "C:/Users/mizr3/Desktop/podcast_downloader", 'subs_only')

6. run script
