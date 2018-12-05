# HQ-Bot
A bot written in Python that predicts the right answer (most of the time) to the questions on the trivia game HQ. Obviously don't use in a live game. The bot basically records the screen of your phone, then uses pytesseract to read the question and the answers, then searches them up using the Google Custom Search API and calculates the likelihood of an answer.
