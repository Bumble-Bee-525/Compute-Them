import requests
import pyautogui as pg
import json

#random functions and stuf
def quoteIt(text, word):
    i = text.find(word)
    if i != -1:
        text = text[:i] + "'" + text[i:i + len(word) - 1] + "'" + text[i + len(word) - 1:]
    return text

def run(currentState):
    #seperate into lines
    currentState["code"] = currentState["code"].split("\n")

    #store blocks
    segmentedCode = []

    #buffers for temporary stuf
    currentBlock = ""
    layers = 0

    '''group code into blocks'''
    i = 0
    while i < len(currentState["code"]):
        line = currentState["code"][i]

        #if it's just a random empty thing get rid of it
        if line == "":
            i += 1
            continue
        # if it's a valid line, continue checking
        else:
            #if it's the end of a block, make a note
            if line[0] == "}":
                layers -= 1
                if len(line) > 2:
                    currentState["code"].insert(i + 1, line[1:])
                    currentState["code"][i] = "}"
                    line = "}"

            #if it's a large block, make a note
            elif ("for" in line) or ("while" in line) or ("if" in line) or ("else" in line):
                layers += 1
            
            #add line to the block
            currentBlock += line + "\n"

        if layers == 0:
            segmentedCode.append(currentBlock)
            currentBlock = ""
        i += 1

    '''Run each segment'''
    prevTrue = False
    for block in segmentedCode:
        #find the first word
        keyCutoff = block.find("(")
        if keyCutoff > block.find("{") and block.find("{") != -1:
            keyCutoff = block.find("{")
        keyword = block[:keyCutoff]

        #if it is a for loop
        if keyword == "for":
            #get how many times it should run
            times = int(block[block.find("<") + 1])

            #run for that many times
            for i in range(times):
                currentState["code"] = block[block.find("{") + 2: block.rindex("}") - 1]
                currentState = run(currentState)
        
        #if it is a while loop
        elif keyword == "while":
            #get the color
            color = block[block.find("(") + 1: block.find("()")].replace("!", "")

            #get the conditional (opposite)
            opposite = block[block.find("(") + 1] == "!"
            
            #XOR helps with !
            #while current color == color ^ conditional
            while (currentState["map"][currentState["y"]][currentState["x"]] == color) ^ opposite:
                currentState["code"] = block[block.find("{") + 2: block.rindex("}") - 1]
                currentState = run(currentState)

        elif keyword == "if":
            #ignores all previous if, else, elseif
            prevTrue = False

            #get the color
            color = block[block.find("(") + 1: block.find("()")].replace("!", "")

            #get the conditional (opposite)
            opposite = block[block.find("(") + 1] == "!"

            if (currentState["map"][currentState["y"]][currentState["x"]] == color) ^ opposite:
                currentState["code"] = block[block.find("{") + 2: block.rindex("}") - 1]
                currentState = run(currentState)
                prevTrue = True
            else:
                prevTrue = False
            
        elif keyword == "elseif" and not prevTrue:
            #get the color
            color = block[block.find("(") + 1: block.find("()")].replace("!", "")

            #get the conditional (opposite)
            opposite = block[block.find("(") + 1] == "!"

            if (currentState["map"][currentState["y"]][currentState["x"]] == color) ^ opposite:
                currentState["code"] = block[block.find("{") + 2: block.rindex("}") - 1]
                currentState = run(currentState)
                prevTrue = True
            else:
                prevTrue = False
            
        elif keyword == "else" and not prevTrue:
            currentState["code"] = block[block.find("{") + 2: block.rindex("}") - 1]
            currentState = run(currentState)
            prevTrue = False
        
        elif keyword == "up":
            #move virtual charcter
            currentState["y"] -= 1
            if currentState["y"] < 0:
                currentState["y"] = len(currentState["map"])

            # pg.keyDown('up')
            # pg.keyUp('up')
            print("goin up")
        
        elif keyword == "down":
            #move virtual charcter
            currentState["y"] += 1
            if currentState["y"] >= len(currentState["map"]):
                currentState["y"] = 0

            # pg.keyDown('down')
            # pg.keyUp('down')
            print("going down")

        elif keyword == "right":
            #move virtual charcter
            currentState["x"] += 1
            if currentState["x"] >= len(currentState["map"][0]):
                currentState["x"] = 0
            
            # pg.keyDown('right')
            # pg.keyUp('right')
            print("going right")
        
        elif keyword == "left":
            #move virtual charcter
            currentState["x"] -= 1
            if currentState["x"] < 0:
                currentState["x"] = len(currentState["map"][0])

            # pg.keyDown('left')
            # pg.keyUp('left')
            print("going left")

        elif prevTrue:
            print("a segment was skipped as its condition wasn't met. No worries. It's all good bruh.")

        else:
            print("some serious shit went down my dude. If an error hasn't been raised, that's even worse, like you're really fucked")

    #return state
    return currentState


#for, while, if, else, else if, 


#open file with all level names ingame
levelFile = open("levelNames.txt")

#scroll file cursor up to current level
level = int(pg.prompt('Type current level:'))
for i in range(level):
    levelFile.readline()

levelnum = level

#main loop
keepGoing = True
while keepGoing:
    #click to focus on to browser
    pg.click(950, 550)

    #read current level name
    currentLevel = levelFile.readline().strip("\n")
    print("current level: ", currentLevel)

    #get the instructions for that level
    level = requests.get("https://compute-it.toxicode.fr/2023-07-03--19-25-27/scripts/challenges/" + currentLevel + ".js").text

    #strip the instructions down
    level = "{" + level[level.find("map"):]
    level = level[:level.find("}", level.find("y: ")) + 1]

    #stringify to json
    #add quotes to keys
    level = quoteIt(level, "map:")
    level = quoteIt(level, "code:")
    level = quoteIt(level, "x:")
    level = quoteIt(level, "y:")
    level = quoteIt(level, "roundedSquares:")
    
    #for actual level instructions, get rid of wierd js syntax like function and {}
    # store the instructions in h, save an empty string as the value for "code"
    i = level.find("function")
    f = level.find("{", i)
    g = level.rindex("}", f, level.rindex("x':"))
    h = level[f + 1:g]
    h = h.replace(" ", "")
    level = level[:i] + "'" + "'" + level[g + 1:]

    #replace all single quotes with doubles for some reason. This breaks if removed. IDK why
    level = level.replace("'", "\"")

    #convert json to a python dictionary
    level = json.loads(level)

    #add the instructions from earlier back in
    level["code"] = h

    #interpret the instructions and run
    run(level)

    #get confirmation on whether or not to keep going
    keepGoing = pg.confirm(text=f"Do you wanna keep going? \nMost recent level complete: {levelnum}", title="no balls?", buttons=["Yes", "No balls"]) == "Yes"
    levelnum += 1

levelFile.close()