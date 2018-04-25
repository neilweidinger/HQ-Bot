from PIL import Image
import pytesseract
import pyscreenshot as ImageGrab
from apiclient.discovery import build
import json
import pprint

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
            line = line.lower().replace("which of these", "what")
            line = line.lower().replace(" never ", " ")
            line = line.lower().replace(" not ", " ")
            question += line + " "
            if '?' in line:
                ans = True
        else:
            if len(line) != 0:
                line = line.lower().replace(" / ", " and ")
                answers.append(line)

    return question, answers


# write data to disk
def writefiles(attempt, num, data):
    filename = createfilename(attempt, num)
    file = open(filename, "w")
    file.write(json.dumps(data, indent=4, ensure_ascii=False))
    file.close()


# create file name depending on attempt and answer number
def createfilename(attempt, num):
    return "data/attempt{}_answer{}.json".format(attempt, num)


# take screenshot and extract text
def read_image():
    im = ImageGrab.grab(bbox=(31,182,470,620))
    # im = Image.open("tests/3.jpg")
    return pytesseract.image_to_string(im)


# calculates and prints out final percentages
def output_answers():

    # find total number of results and total number of occurrences for all answers
    total_num_occurrences = sum(f_results[key][0] for key in f_results)
    total_num_results = sum(f_results[key][1] for key in f_results)
    total_num_ans_occurrences = sum(f_results[key][2] for key in f_results)

    print(question)

    # loops through main data dictionary (dict value aka nums is a list)
    for answer, nums in f_results.items():
        occurrences_percentage = 0
        results_percentage = 0
        ans_occurrences_percentage = 0

        # if statements to avoid division through 0 error
        if (total_num_occurrences > 0):
            occurrences_percentage = nums[0] / total_num_occurrences
        if (total_num_results > 0):
            results_percentage = int(nums[1]) / total_num_results
        if (total_num_ans_occurrences > 0):
            ans_occurrences_percentage = nums[2] / total_num_ans_occurrences

        # print(answer + " --- " + str(nums[0]) + " --- " + str(nums[1]))
        print("{}".format(answer))
        print(str((ans_occurrences_percentage + results_percentage +
                   occurrences_percentage) / 3 * 100) + "\n")

    print(f_results)

# receive data from Google cse and return data in form of dictionary
def attempt_two_three():

    # build service object to interact with Google api
    service = build("customsearch", "v1", developerKey=g_cse_api_key)

    # manually override and edit answers and question
    # global question
    # question = "What kind of tax does apply in the regular edition of monopoly "
    # answers[0] = "Ireland"
    # answers[1] = "Diff'rent Strokes"
    # answers[2] = "Scotland"

    for i in range(3):

        # pull data from Google cse 
        google_data = service.cse().list(q=question + answers[i], cx=g_cse_id).execute()

        # or alternatively use sample/already saved data (doens't count against api quota)
        # json_file = open("data/data" + str(i) + ".json", "r", encoding="utf-8")
        # google_data = json.load(json_file)

        # save data to disk in json format
        writefiles(attempt="2_3", num=str(i), data=google_data)
        
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

                # search through metatags, try for just in case metatags don't exist
                try:
                    for key in item["pagemap"]["metatags"][0].keys():
                        num_occurrences += item["pagemap"]["metatags"][0][key].lower().count(answers[i].lower())
                except:
                    continue

        # just in case we try to access a nonexistent "item" above bc search didn't return anything
        except KeyError:
            print("search for {} returned no results".format(answers[i]))

        f_results[answers[i]].append(int(google_data["searchInformation"]["totalResults"]))
        f_results[answers[i]].append(num_occurrences)

    return f_results

def attempt_one():

    # build service object to interact with Google api
    service = build("customsearch", "v1", developerKey=g_cse_api_key)

    # store results in this dictionary
    results = {}

    # Manually override and edit answers and question
    # global question
    # question = "What kind of tax does apply in the regular edition of monopoly "
    # answers[0] = "Ireland"
    # answers[1] = "Diff'rent Strokes"
    # answers[2] = "Scotland"

    # pull data from Google cse 
    google_data = service.cse().list(q=question, cx=g_cse_id).execute()

    # save data to disk in json format
    writefiles(attempt=1, num="_all", data=google_data)

    for i in range(3):

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

                # search through metatags, try for just in case metatags don't exist
                try:
                    for key in item["pagemap"]["metatags"][0].keys():
                        num_occurrences += item["pagemap"]["metatags"][0][key].lower().count(answers[i].lower())
                except:
                    continue

        # just in case we try to access a nonexistent "item" above bc search didn't return anything
        except KeyError:
            print("search for {} returned no results".format(answers[i]))

        results[answers[i]] = [num_occurrences]

    return results


if __name__ == "__main__":

    # separate question and answers from text
    question, answers = parse_question(read_image())
    print(question)
    print(answers, end="\n\n")

    # get data from Google
    f_results = attempt_one()
    attempt_two_three()

    # print results
    output_answers()
