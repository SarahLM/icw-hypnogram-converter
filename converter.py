# %%
from edfrd import read_header, read_data_records
import json
import xml.etree.ElementTree as ET
import csv
import argparse


# *************************If the file originated of CMPStudy********************************************************
def readcmpstudy(parameter):
    tree = ET.parse(inputfile)
    root = tree.getroot()

    signalinput = []
    sleepstages = []

    # get the Durationtime

    for child in root.findall("./EpochLength"):
        durationxml = "".join(child.itertext())
        print("Dauer " + durationxml)

    # reading input tags

    for child in root.findall("./ScoredEvents"):
        # print(list(child))
        for chil in child.findall("./ScoredEvent"):
            # print(list(chil))
            for chi in chil.findall("./Input"):
                inputs = "".join(chi.itertext())
                # for i in enumerate(inputs):
                signalinput.append(inputs)

    # get the SleepStages
    for child in root.findall("./SleepStages"):
        # print(list(child))
        for chil in child.findall("./SleepStage"):
            stages = "".join(chil.itertext())
            # for i in enumerate(stages):
            sleepstages.append(stages)

    functionmapping(sleepstages, durationxml, parameter)


# ***************************************If the file originated from Respironics********************************************************
def readrespironics(parameter):
    secondtree = ET.parse(inputfile)
    secondroot = secondtree.getroot()

    sleepstages = []

    # print(secondroot.tag)
    # print(list(secondroot))

    # GET SLEEPSTAGES

    for child in secondroot.findall("./{http://www.respironics.com/PatientStudy.xsd}ScoringData"):
        # print(list(child))
        for chil in child.findall("./{http://www.respironics.com/PatientStudy.xsd}StagingData"):
            #   print(list(chil))
            for chi in chil.findall("./{http://www.respironics.com/PatientStudy.xsd}UserStaging"):
                #            print(list(chi))
                for ch in chi.findall("./{http://www.respironics.com/PatientStudy.xsd}NeuroAdultAASMStaging"):
                    #             print(list(ch))
                    for c in ch.findall("./{http://www.respironics.com/PatientStudy.xsd}Stage"):
                        inputa = c.get("Type")
                        for i in enumerate(inputa):
                            sleepstages.append(inputa)
    functionmapping(sleepstages, "unknown", parameter)


# convert edf to json
# %%

# ***************************************If the file originated from CDatentechnik********************************************************
def readcdatentechnik(parameter):
    file_path = inputfile
    # changedLists = []

    header = read_header(file_path)
    # %%
    l = []
    for i, data_record in enumerate(read_data_records(file_path, header)):
        sleep_stage = data_record[0][0]
        l.append(sleep_stage.tolist())

        _ = read_data_records(
            file_path,
            header,
            start=0,
            end=header.number_of_data_records
        )
    functionmapping(l, "unknown", parameter)


# ***************************************If the file originated from RemLogic********************************************************
def readunknowncsv(parameter):
    stadiensleep = []
    print(parameter)

    with open(inputfile, 'r', newline='') as csvDataFile:
        csv_reader_object = csv.reader(csvDataFile)
        for index, row in enumerate(csv_reader_object):
            if index > 1:
                stadiensleep.append(row[0])

    functionmapping(stadiensleep, "unknown", parameter)


# Create the new converted json
def functionjson(stadien, period):
    # Read in template for hlhir format
    if stadien != None:
        with open('template.json', 'r') as json_file:
            hlhir = json.load(json_file)
            hlhir['valueSampledData']['data'] = stadien
            hlhir['effectiveDateTime'] = "test"
            hlhir['valueSampledData']['period'] = period

        with open("Ausgabedateien/" + outputfile, "w") as write_file:
            json.dump(hlhir, write_file, indent=2)
        print("File converted")
    else:
        print("failed, because stages are empty")

# mapping sleepstages on LOINC Format
def functionmapping(maplist, givenperiod, parameter):
    convlist = []

    def switch_stages(mapped):
        global switcher
        if parameter == "UnknownCSV":
            switcher = {
                # corresponds to Sleep stage unspecified in Loinc
                "10": 23664,
                "11": 23672,
                "12": 23680,
                # "RemSpindle": 23688,
                "13": 23696,
                "14": 23704,
                "15": 23712,
            }
        if parameter == "CDatentechnik":
            switcher = {
                # corresponds to Sleep stage unspecified in Loinc
                # Zuordnung muss nochmals überprüft werden
                9: 23656,
                6: 23664,
                0: 23672,
                5: 23680,
                7: 23688,
                1: 23696,
                2: 23704,
                3: 23712,
                4: 23720,
            }
        if parameter == "CMPStudy":
            switcher = {
                "9": 23656,
                "6": 23664,
                "0": 23672,
                "5": 23680,
                "7": 23688,
                "1": 23696,
                "2": 23704,
                "3": 23712,
                "4": 23720
            }
        if parameter == "Respironics":
            switcher = {
                # equals Sleep stage unspecified in Loinc
                "NotScored": 23656,
                "": 23664,
                "Wake": 23672,
                "REM": 23680,
                "RemSpindle": 23688,
                "NonREM1": 23696,
                "NonREM2": 23704,
                "NonREM3": 23712,
                "NonREM4": 23720,
            }
        convlist.append(switcher.get(mapped, stage))

    for stage in maplist:
        switch_stages(stage)
    functionjson(convlist, givenperiod)


def recognize():
    parameter = None
    ergebnis = None
    originfile = open(inputfile, 'r')
    # print(datei.read(30))
    ergebnis = originfile.read(150)

    if "X,,4,09.05.1999,21:55:42,10.05" in ergebnis:
        parameter = "UnknownCSV"
        readunknowncsv(parameter)
    elif "<CMPStudyConfig>" in ergebnis:
        parameter = "CMPStudy"
        readcmpstudy(parameter)
    elif "www.respironics.com" in ergebnis:
        parameter = "Respironics"
        readrespironics(parameter)
    elif "Converted by EDFtoEDF CDatentechnik" in ergebnis:
        parameter = "CDatentechnik"
        readcdatentechnik(parameter)
    else:
        print("nicht zulässiger Dateityp")

# ***********Build query and leave fixed variables in json************************************************************************

if __name__ == "__main__":
    date = None
    period = None

    parser = argparse.ArgumentParser()
    # parser.add_argument("Herkunft", type=str, help="Herkunftssystem der Datei")
    parser.add_argument("Dateiname", help="Name der zu konvertierenden Datei")
    argsdefault = parser.parse_args()
    parser.add_argument("Output", type=str, help="Name der neuen Datei", nargs="?", default=argsdefault.Dateiname+".json")

    args = parser.parse_args()
    inputfile = args.Dateiname
    # parameter = args.Herkunft
    outputfile = args.Output
    recognize()
    print(args)

