from PIL import Image, ImageEnhance
import pytesseract
import pyscreenshot as ImageGrab
from apiclient.discovery import build
import json
import re
import time

g_cse_api_key = "***REMOVED***"
# g_cse_id = "007453928249679215123:dhdhqg4tpxi" # emphasizes a few sites
# g_cse_id = "007453928249679215123:ynpo3pdphmg" # everything
# g_cse_id = "007453928249679215123:zrrhksiiyh8" # no wikipedia
g_cse_id = "007453928249679215123:iisyb2-ac_s" # first engine but no dictionaries or thesauruses


# parse ocr text to get question as string and answers as list
def parse_question(ocr_text):
    lines = ocr_text.splitlines()
    question = ""
    answers = []
    is_not = False

    # for quizbiz
    # lines[0] = lines[0][3:]

    ans = False
    for line in lines:
        if not ans:

            # checks to see if question is an "is not" question
            if re.match(r"(?i)(.*)\bNOT\b(.*)", line):
                is_not = True

            # replaces "which of these" or just "which" with "what"
            line = re.sub(r"(?i)\bWhich of these\b|\bWhich\b", "what", line)
            # replaces "never" with a space
            line = re.sub(r"(?i)\bNever ?", "", line)
            # takes out all occurrences of a "not"
            line = re.sub(r"(?i)\bNOT ?", "", line)

            # only add non-empty lines to question
            if len(line) > 0:
                question += line + " "
            # if we encounter a "?", that means answers are coming up in the text
            if '?' in line:
                ans = True
        else:
            if len(line) != 0:
                # replaces "/" with "and"
                line = re.sub(r"/", "and", line)
                answers.append(line)

    return question, answers, is_not


# write data to disk
def writefiles(attempt, num, data):
    filename = "data/attempt{}_answer{}.json".format(attempt, num)
    file = open(filename, "w")
    file.write(json.dumps(data, indent=4, ensure_ascii=False))
    file.close()


# take screenshot and extract text
def read_image():

    # Capture image
    image = ImageGrab.grab(bbox=(31,184,470,620))
    # image = ImageGrab.grab(bbox=(33,205,463,590))
    # image = Image.open("tests/3.jpg")

    # Increase contrast
    Contraster = ImageEnhance.Contrast(image)
    image = Contraster.enhance(3)

    # tesseract recognizes text and outputs it as a string
    return pytesseract.image_to_string(image)


# calculates and prints out final percentages
def output_answers():

    # find total number of results and total number of occurrences for all answers
    total_num_occurrences = sum(results[key][0] for key in results)
    total_num_results = sum(results[key][1] for key in results)
    total_num_ans_occurrences = sum(results[key][2] for key in results)

    print(question)

    # list to keep track of answer and corresponding percentage most likely to be correct
    predicted_percentage = [0, "", False]

    # loops through main data dictionary (dict value aka nums is a list)
    for answer, nums in results.items():
        occurrences_percentage = 0
        results_percentage = 0
        ans_occurrences_percentage = 0

        # if statements to avoid division through 0 error, then find decimal percentage
        if (total_num_occurrences > 0):
            occurrences_percentage = nums[0] / total_num_occurrences
        if (total_num_results > 0):
            results_percentage = int(nums[1]) / total_num_results
        if (total_num_ans_occurrences > 0):
            ans_occurrences_percentage = nums[2] / total_num_ans_occurrences

        # finds overall percentage by averaging all percentages (results % not weighted as much)
        overall_percentage = (ans_occurrences_percentage + (results_percentage * .75) +
                              occurrences_percentage) / 3 * 100

        # track most likely answer
        if not is_not and overall_percentage > predicted_percentage[0]:
            predicted_percentage[0] = overall_percentage
            predicted_percentage[1] = answer
        elif is_not:
            if not predicted_percentage[2] or overall_percentage < predicted_percentage[0]:
                predicted_percentage[2] = True
                predicted_percentage[0] = overall_percentage
                predicted_percentage[1] = answer

        print("{}".format(answer))
        print("{:5.2f} --- {:5.2f} --- {:5.2f}".format(occurrences_percentage * 100, 
                                                       results_percentage * 100,
                                                       ans_occurrences_percentage * 100))
        print("{:5.2f} \n".format(overall_percentage))

    # prints out most likely answer
    print("\033[4;32m{} --- {}\033[0m".format(predicted_percentage[1], predicted_percentage[0]))

    print(results)


def search_occurences(new_data, ans_num):

        # find number of occurrences of answer in retrieved data
        num_occurrences = 0

        # properties that will be searched for number of occurrences
        property_list = ["link", "title", "snippet", "htmlSnippet", 
                         "formattedUrl", "htmlFormattedUrl"]

        try:
            for item in new_data["items"]:
                # if "wikipedia" in item["link"]:
                #     continue
                for property in property_list:
                    num_occurrences += item[property].lower().count(answers[ans_num].lower())

                # search through metatags, try for just in case metatags don't exist
                try:
                    for key in item["pagemap"]["metatags"][0].keys():
                        num_occurrences += item["pagemap"]["metatags"][0][key].lower().count(answers[ans_num].lower())
                except:
                    continue

        # just in case we try to access a nonexistent "item" above bc search didn't return anything
        except KeyError:
            print("search for {} returned no results".format(answers[ans_num]))

        return num_occurrences


def attempt_one():

    # build service object to interact with Google api
    service = build("customsearch", "v1", developerKey=g_cse_api_key)

    # pull data from Google cse 
    google_data = service.cse().list(q=question, cx=g_cse_id).execute()

    # save data to disk in json format
    writefiles(attempt=1, num="_all", data=google_data)

    for i in range(3):

        num_occurrences = search_occurences(new_data=google_data, ans_num=i)

        results[answers[i]] = []
        results[answers[i]].append(num_occurrences)


# receive data from Google cse and return data in form of dictionary
def attempt_two_three():

    # build service object to interact with Google api
    service = build("customsearch", "v1", developerKey=g_cse_api_key)

    for i in range(3):

        # pull data from Google cse 
        google_data = service.cse().list(q=question + answers[i], cx=g_cse_id).execute()

        # or alternatively use sample/already saved data (doens't count against api quota)
        # json_file = open("data/data" + str(i) + ".json", "r", encoding="utf-8")
        # google_data = json.load(json_file)

        # save data to disk in json format
        writefiles(attempt="2_3", num=str(i), data=google_data)
        
        num_occurrences = search_occurences(new_data=google_data, ans_num=i)

        results[answers[i]].append(int(google_data["searchInformation"]["totalResults"]))
        results[answers[i]].append(num_occurrences)


if __name__ == "__main__":

    start = time.time()

    # separate question and answers from text
    question, answers, is_not = parse_question(read_image())
    print(question)
    print(answers, end="\n\n")

    # manually override and edit answers and question
    # question = "Who has played in both the Super Bowl and the World Series? "
    # answers[0] = "Bo Jackson"
    # answers[1] = "Brian Jordan"
    # answers[2] = "Deion Sanders"

    # get data from Google
    results = {}
    attempt_one()
    print("{} --- {}".format("attempt one", time.time() - start))
    attempt_two_three()
    print("{} --- {}".format("attempt two", time.time() - start))

    # print results
    output_answers()
    print("{} --- {}".format("final", time.time() - start))
