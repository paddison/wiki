import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def convertMd(string):
    def handleHeader(arr):
        for i, string in enumerate(arr):
            if string == "": continue
            if re.search("^#+\s", string):
                headerLvl = len(string) - len(string.lstrip('#'))
                if headerLvl > 6: 
                    continue
                regex = "^"
                for r in range(headerLvl):
                    regex = regex + "#"
                regex = regex+ "\s"
                string = re.sub(regex, f"<h{headerLvl}>", string) + f"</h{headerLvl}>"
                arr[i] = string
        return arr

    def handleUList(arr):
        regex = "(^\s*\*\s)|(^\s*-\s)"
        isList = False   
        for i, string in enumerate(arr):
            if string == "": continue
            if not isList:
                if re.search("(^\*\s)|(^-\s)", string):
                    isList = True
                    curWs = 0
                    string = "<ul><li>" + re.sub("(^\*(?=[^*]))|(^-(?=[^-]))", "", string).lstrip() + "</li>"
            else:
                if re.search(regex, string):
                    ws  = len(string) - len(string.lstrip(' '))
                    if ws == curWs + 2:
                        string = "<ul><li>" + re.sub(regex, "", string) + "</li>"
                        curWs = ws
                    elif ws == curWs:
                        string = "<li>" + re.sub(regex, "", string) + "</li>"
                    elif ws < curWs:
                        if ws % 2 != 0:
                            ws += 1
                        ulTags = ""
                        for r in range(int((curWs - ws) / 2)):
                            ulTags += "</ul>"   
                        string = ulTags + "<li>" + re.sub(regex, "", string) + "</li>"
                        curWs = ws
                else:
                    string = "</ul>" + string
                    isList = False

            arr[i] = string

    def handleBold(arr):
        for i, string in enumerate(arr):
            if string == "": continue
            matches = re.findall("(\*\*[^*]+\*\*)|(__[^_]+__)", string)
            for match, none in  matches:
                match = "<strong>" + re.sub("(\*\*)|(__)", "", match) + "</strong>"
                string = re.sub("(\*\*[^*]+\*\*)|(__[^_]+__)", match, string, 1)
            arr[i] = string

    def handleItalic(arr):
        for i, string in enumerate(arr):
            if string == "": continue
            matches = re.findall("((?<=[^*])\*[^*]+\*(?=[^*]))|((?<=[^_])_[^_]+_(?=[^_]))", string)
            for match, none in  matches:
                match = " <em>" + re.sub("(\*)|(_)", "", match) + "</em> "
                string = re.sub("([^*]\*[^*]+\*[^*])|([^_]_[^_]+_[^_])", match, string, 1)
            # string = re.sub("\*\*(?=[^*]+\*\*)", "<strong>", string)
            arr[i] = string

    def handleLinks(arr):
        for i, string in enumerate(arr):
            if string == "": continue
            matches = re.findall("\[.*?\]\(.*?\)", string)
            for match in matches:
                href = re.findall("(?<=\().*?(?=\))", match)[0]
                name = re.findall("(?<=\[).*?(?=\])", match)[0]
                print(href, name)
                match = "<a href=" + href + ">" + name + "</a>"
                string = re.sub("\[.*?\]\(.*?\)", match, string, 1)
            arr[i] = string

    def handlePara(arr):
        for i, string in enumerate(arr):
            if string == "": continue
            if re.search("^(?!\s*\*\s)", string) and re.search("^(?!\s*#+\s)", string):
                string = "<p>" + string + "</p>"
                arr[i] = string

    lineArr = string.splitlines()

    handlePara(lineArr)
    handleHeader(lineArr)
    handleUList(lineArr)
    handleBold(lineArr)
    handleItalic(lineArr)
    handleLinks(lineArr)

    return "\n".join(lineArr)
