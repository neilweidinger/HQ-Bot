# HQ-Bot
A bot written in Python that predicts the right answer (most of the time) to the questions on the trivia game HQ. The bot basically records the screen of your phone, then uses pytesseract to read the question and the answers, then searches them up using the Google Custom Search API and calculates the likelihood of an answer. Obviously don't use in a live game.

## Requirements
Tested using Python 3.7

Install requirements using pip:
```
$ pip3 install -r requirements.txt
```
Also install tesseract:
```
$ brew install tesseract
```

Change `key.config.example` to just `key.config` and put in your Google Custom Search API Key in the file.

## Usage
Make sure your recording of the HQ game is in the top left corner of your screen, otherwise the bot won't correctly read off the questions and answers. Also this has only been tested on an iPhone 6s, so the image capture parameters might have to be adjusted to get it to work. 

Since all the bot really does is take a screenshot of your computer screen, it's actually irrelevant if you're mirroring your phone or just playing back a video stored on your computer. If you want to mirror your phone on your computer (iPhones used with macs, not sure about platforms), plug your phone in, open up QuickTime, and click the little arrow next to the red record button. From the dropdown select your phone, and your phone should be mirrored on your computer now.

When the question and answers are displayed on the app, run
```
$ python script.py
```
and it will tell you what it thinks is the most likely answer.

## Screenshots
![example1](https://i.imgur.com/beRFiwN.jpg)
*Bot predicted Starry Night; Starry Night was the correct answer*
