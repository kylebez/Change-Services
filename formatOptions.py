# Written by Kyle Beswick
# Function formatting console for user input
# strs is list of strings to display as options
# multi is boolean to allow multiple selections
# back is boolean to allow going to previous menu - a return option will return 0
# returns list of int

def getOptionString(strs, multi=False, back=True):
    oS = ""
    strsl = len(strs)
    if strsl>1:
        numop = range(1, strsl+1)
    else:
        numop = [1]
    if len(numop) != strsl:
        print " Error in range"
        return -1
    i=0
    for s in strs:
        oS+="\n ["+str(numop[i])+"] "+s
        i+=1 
    if back is True:
        oS+="\n ----- \n [0] RETURN"
        numop.append(0)
    print oS
    if multi is False:
        applyScope = raw_input("\n Make selection: ")        
        while True:
            try:
                applyScope = int(applyScope)
            except ValueError:
                applyScope = raw_input("\n Non-numerical value detected - enter again: ")
                continue
            break
        while applyScope not in numop:
            applyScope = raw_input("\n Not in range - make selection: ")
            try:
                applyScope = int(applyScope)
            except ValueError:
                applyScope = raw_input("\n Non-numerical value detected - enter again: ")
                continue
        applyScope = [applyScope]
    elif multi is True:
        applyScope = multiValues(numop)        
    else:
        return -1    
    return applyScope

#handling a multi selection string
def multiValues(n):
    opts = raw_input("\n Make selection (multiple allowed - comma seperated and/or hyphenated range): ")
    if opts == 0:
        return opts
    optsa = []
    opts = opts.split(',')
    for s in opts:
        s = s.strip()
        s = s.split('-',1)
        if len(s)>1:
            try:
                s1 = int(s[0])
                s2 = int(s[1])
                s2 = s2+1
            except Exception as e:
                print e
            s = range(s1,s2)
            for ss in s:
                #ss = ss.strip
                #print str(ss) + " detected"
                if ss not in n:
                    print "\n " + str(ss) + " is not in range. Enter selection range again: "
                    se = multiValues(n)
                    # print "\n Inside recursion" #
                    return se
                if ss != 0:
                    optsa.append(ss)
        else:
            try:
                s1 = int(s[0])
                optsa.append(s1)
            except:
                print "\n " + str(s[0]) + " is not in range. Enter selection range again: "
                se = multiValues(n)
                # print "\n Inside recursion" #
                return se
    return optsa        
            
                
