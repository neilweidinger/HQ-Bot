from PIL import Image, ImageEnhance
import pytesseract
import pyscreenshot as ImageGrab
from apiclient.discovery import build
import json
import cv2
import numpy

g_cse_api_key = "***REMOVED***"
g_cse_id = "007453928249679215123:dhdhqg4tpxi" # emphasizes a few sites
# g_cse_id = "007453928249679215123:ynpo3pdphmg" # everything
# g_cse_id = "007453928249679215123:zrrhksiiyh8" # no wikipedia


# parse ocr text to get question as string and answers as list
def parse_question(ocr_text):
    lines = ocr_text.splitlines()
    question = ""
    answers = []

    ans = False
    for line in lines:
        if not ans:
            print(line)
            line = line.lower().replace("which of these", "what")
            line = line.lower().replace(" never ", " ")
            # line = line.lower().replace(" not ", " ")
            print(line)
            question += line + " "
            if '?' in line:
                ans = True
        else:
            if len(line) != 0:
                answers.append(line)

    return question, answers


# write data to disk
def writefiles(num, data):
    filename = "data/data" + num + ".json"
    file = open(filename, "w")
    file.write(json.dumps(data, indent=4, ensure_ascii=False))
    file.close()


# take screenshot and extract text
def read_image():

    # Capture image
    image = ImageGrab.grab(bbox=(31,184,470,620))
    # image = Image.open("tests/3.jpg")

    # Increase contrast
    Contraster = ImageEnhance.Contrast(image)
    image = Contraster.enhance(3)

    # # Increase sharpness
    # Sharpener = ImageEnhance.Sharpness(image)
    # image = Sharpener.enhance(2)


    cvimage = numpy.array(image)
    image = cv2.cvtColor(cvimage, cv2.COLOR_BGR2GRAY)
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    cv2.imshow("image", image)
    cv2.waitKey(0)

    return pytesseract.image_to_string(image)


# calculates and prints out final percentages
def output_answers():

    # find total number of results and total number of occurrences for all answers
    total_num_results = sum(results[k][0] for k in results)
    total_num_occurrences = sum(results[k][1] for k in results)

    print(question)

    # loops through main data dictionary (dict value aka nums is a tuple)
    for answer, nums in results.items():
        results_percentage = 0
        occurrences_percentage = 0

        # if statements to avoid division through 0 error
        if (total_num_results > 0):
            results_percentage = int(nums[0]) / total_num_results
        if (total_num_occurrences > 0):
            occurrences_percentage = nums[1] / total_num_occurrences

        print(answer + " --- " + str(nums[0]) + " --- " + str(nums[1]))
        print(str(results_percentage) + " --- " + str(occurrences_percentage))
        print(str((occurrences_percentage + results_percentage) / 2 * 100) + "\n")


# receive data from Google cse and return data in form of dictionary
def search_up():

    # build service object to interact with Google api
    service = build("customsearch", "v1", developerKey=g_cse_api_key)

    # store results in this dictionary
    results = {}

    # manually override and edit answers and question
    # global question
    # question = "according to its inventor, the graphics format spelled g-i-f is pronounced how? "
    # answers[0] = "Ireland"
    # answers[1] = "\"jif\""
    # answers[2] = "Scotland"

    for i in range(3):

        # pull data from Google cse 
        google_data = service.cse().list(q=question + answers[i], cx=g_cse_id).execute()

        # or alternatively use sample/already saved data (doens't count against api quota)
        # json_file = open("data/data" + str(i) + ".json", "r", encoding="utf-8")
        # google_data = json.load(json_file)

        # save data to disk in json format
        writefiles(str(i), google_data)
        
        # find number of occurrences of answer in retrieved data
        num_occurrences = 0

        # properties that will be searched for number of occurrences
        property_list = ["link", "title", "snippet", "htmlSnippet", 
                         "formattedUrl", "htmlFormattedUrl"]

        try:
            for item in google_data["items"]:
                # if "wikipedia" not in item["link"]:
                for property in property_list:
                    num_occurrences += item[property].lower().count(answers[i].lower())
        # just in case we try to access a nonexistent "item" above bc search didn't return anything
        except KeyError:
            print("search for {} returned no results".format(answers[i]))

        results[answers[i]] = (int(google_data["searchInformation"]["totalResults"]), num_occurrences)

    return results


if __name__ == "__main__":

    # separate question and answers from text
    question, answers = parse_question(read_image())
    print(question)
    print(answers, end="\n\n")

    # get data from Google
    results = search_up()

    # print results
    output_answers()
