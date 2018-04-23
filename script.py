from PIL import Image
import pytesseract
import pyscreenshot as ImageGrab
from apiclient.discovery import build
import pprint
import json

g_cse_api_key = "***REMOVED***"
g_cse_id = "007453928249679215123:dhdhqg4tpxi"


# parse ocr text to get question as string and answers as list
def parse_question(ocr_text):
    lines = text.splitlines()
    question = ""
    answers = []

    ans = False
    for line in lines:
        if not ans:
            question += line + " "
            if line[len(line) - 1] == '?':
                ans = True
        else:
            if len(line) != 0:
                answers.append(line)

    return question, answers


# im = ImageGrab.grab(bbox=(31,180,470,620))
im = Image.open("tests/4.jpg")
text = pytesseract.image_to_string(im)

# separate question and answers from text
question, answers = parse_question(text)

# seach up
service = build("customsearch", "v1", developerKey=g_cse_api_key)
num_results = {}

for i in range(3):
    res = service.cse().list(q=question + answers[i], cx=g_cse_id).execute()
    num_results[answers[i]] = (res["searchInformation"]["formattedTotalResults"])

    filename = "data" + str(i) + ".json"
    file = open(filename, "w")
    file.write(json.dumps(res))
    file.close()

print(question)
for a, n in num_results.items():
    print(a + " --- " + n)
