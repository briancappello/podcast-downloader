readme for podcast_downloader.py

windows:
1. create folder where you want output files (subtitle text, audio tracks) to be (ex desktop\podcast_subs)

virtualenv method
2. place python script (podcast_downloader.py) in folder you created
3. open command prompt (windows key > "cmd" > enter)
4. create virtual environment
4a. cd to folder created (ex. cd desktop\podcast_subs)
4b. py-m venv env
4c. .\env\Scripts\activate
5. install dependencies (click, youtube-dl, etc)
ex. pip install click
6. call file, pass arguments in
ex. python podcast_downloader.py "https://www.youtube.com/watch?v=bLDpJO795Os", "C:/Users/mizr3/Desktop/podcast_downloader", 'subs_only'

IDE & shell method
2. opens script in your IDE
3. install dependencies (click, youtube-dl, etc)
4. comment "click." lines and "if __name__" section
5. add line at end to call the main function
main("https://www.youtube.com/watch?v=bLDpJO795Os", "C:/Users/mizr3/Desktop/podcast_downloader", 'subs_only')
6. run script