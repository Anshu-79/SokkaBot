import json

file = open("announcements.json", "r")
file_data = json.load(file)


def getDictByTicketID(tid):
    file = open("announcements.json", "r")
    file_data = json.load(file)

    if len(file_data) != 0:
        for d in file_data:
            if d["ticket_id"] == tid:
                return d
        return None

    else:
        return None


def updateDictByTicketID(tid, new_dict):
    myDict = getDictByTicketID(tid)
    file = open("announcements.json", "w")
    file_data = json.load(file)

    if len(file_data) != 0:
        i = file_data.index(myDict)
        print(file_data)
        file_data[i].update(new_dict)
        print("this ", file_data)

        json.dump(file_data, file, indent=2)
