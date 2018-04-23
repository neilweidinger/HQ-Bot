from PIL import Image
import pytesseract
import pyscreenshot as ImageGrab
from apiclient.discovery import build
import pprint
import json

g_cse_api_key = "***REMOVED***"
# g_cse_id = "007453928249679215123:dhdhqg4tpxi"
g_cse_id = "007453928249679215123:ynpo3pdphmg"

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

# write data to disk
def writefiles(num, data):
    filename = "data/data" + num + ".json"
    file = open(filename, "w")
    file.write(json.dumps(res, indent=4, ensure_ascii=False))
    file.close()

# im = ImageGrab.grab(bbox=(31,180,470,620))
im = Image.open("tests/14.jpg")
text = pytesseract.image_to_string(im)

# separate question and answers from text
question, answers = parse_question(text)
print(question)
print(answers)

# seach up
service = build("customsearch", "v1", developerKey=g_cse_api_key)
results = {}
total_num_occurrences = 0
total_num_results = 0

for i in range(3):
    res = service.cse().list(q=question + answers[i], cx=g_cse_id).execute()
    # json_file = open("sampledata/d" + str(i) + ".json", "r", encoding="utf-8")
    # res = json.load(json_file)
    
    # find number of occurrences of answer in retrieved data
    num_occurrences = 0

    # properties that will be searched for number of occurrences
    property_list = ["link", "title", "snippet", "htmlSnippet", "formattedUrl", "htmlFormattedUrl"]

    for item in res["items"]:
        for property in property_list:
            num_occurrences += item[property].lower().count(answers[i].lower())

    results[answers[i]] = (res["searchInformation"]["totalResults"], num_occurrences)
    total_num_results += int(res["searchInformation"]["totalResults"])
    total_num_occurrences += num_occurrences
    
    writefiles(str(i), res)

print(question)
for answer, nums in results.items():
    results_percentage = 0
    occurrences_percentage = 0
    if (total_num_results > 0):
        results_percentage = int(nums[0]) / total_num_results
    if (total_num_occurrences > 0):
        occurrences_percentage = nums[1] / total_num_occurrences

    print(answer + " --- " + str(nums[0]) + " --- " + str(nums[1]))
    print(str(results_percentage) + " --- " + str(occurrences_percentage))
    print(str((occurrences_percentage + results_percentage) / 2 * 100) + "\n")
