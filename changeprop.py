# Code built from template written by ESRI
# Code modifications and additions and console navigation by Kyle Beswick

# For Http calls
import httplib, urllib, urllib2, json, contextlib

#import other functions
import formatOptions as forop

# Defines the entry point into the script
def main(argv=None):
    
    username = raw_input(" Enter username: ")
    password = raw_input(" Enter password: ")
    # Ask for server name
    serverName = raw_input(" Enter server name (or ip): ")
    serverPort = 6080   
    
    # Get a token
    token = getToken(username, password, serverName, serverPort, 60)
    if token == "":
        print " Could not generate a token with the username and password provided."    
        return
    elif token == -1:
        print " FUNCTION ERROR"
        return
    
    # This request only needs the token and the response formatting parameter 
    params = urllib.urlencode({'token': token, 'f': 'json'})    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    #Sets the selection scope
    def firstSelect(url,tok):
        rootservices = None
        folderservices = None
        allservices = getCatalog(url, tok)
        if allservices == -1:
            print " FUNCTION ERROR"
            return
        rootservices = allservices['services']
        folders = allservices['folders']
        optlist = ["View root folder services"]
        if len(folders) > 1:        
            optlist.append("View list of folders")
        options = forop.getOptionString(optlist,back=False)
        if options == -1:
            print " FUNCTION ERROR"
            return
        secondSelect(options[0],url,tok,rootservices,folders)
        return
    
    def secondSelect(fs,url,tok,rs,f):
        global serviceSelect
        global servicelist
        if fs == 1: #root selected
            serviceSelect = getServiceOptions(rs)  
       
        elif fs == 2: #folders selected
            foptions = forop.getOptionString(f)
            if foptions[0] == 0:
                firstSelect(url,tok)
                return
            #selectedFolder = folders[foptions[0]-1]
            fservices = getCatalog(url+"/"+f[foptions[0]-1],tok)
            if fservices == -1:
                print "FUNCTION ERROR"
                return
            folderservices = fservices['services']            
            serviceSelect = getServiceOptions(folderservices)
            if serviceSelect[0] == 0:
                secondSelect(fs,url,tok,rs,f)
                return            
        if folderservices is None:
            selectedFolder = rootservices
        else:
            selectedFolder = folderservices
        servicelist = map(lambda i: selectedFolder[i-1],serviceSelect)
        #print servicelist #
        return
        #elif options[0] == 3: #view all selected - REMOVE THIS??  

    firstSelect(baseurl, token)          
    
    properties = enterData() 
    
    #print "Services selected: " + serviceSelect   
    
    print "\n Services being modified: "
    for serv in servicelist:
        print " "+serv['folderName']+":"+serv["serviceName"]
    print "\n"
    for serv in servicelist:
        changed = changeServiceProperties (serverName,serverPort,serv["serviceName"],serv["type"],serv['folderName'],properties,token)
        if changed == 0:
           print " "+serv["serviceName"]+" had an error"
    print " All services completed - check any errors above"


# Function assigning user input
def enterData():    

    #Set instances
    mnI = raw_input("\n Enter the new minimum # of instances: ")
    mxI = raw_input("\n Enter the new maximum # of instances: ")

    #Set wait time
    wT = raw_input("\n Enter the maximum time a client will wait (seconds): ")

    #Set max idle time
    iT = raw_input("\n Enter the maximum time an idle instance will run (seconds): ")

    #Set usage time
    uT = raw_input("\n Enter the maximum time a client can use an instance (seconds): ")

    #Set isolation level
    iM = raw_input("\n Low or high isolation? ").upper()
    while (iM != 'LOW' and iM != 'HIGH'):
        print " Not valid entry"
        iM = raw_input("Low or high isolation? ").upper()

    # Check to make sure values are valid
    while True:
        try:
            minINum = int(mnI)
            maxINum = int(mxI)
            wTNum = int(wT)
            iTNum = int(iT)
            uTNum = int(uT)
            break
        except ValueError:
            print "\n Numerical value not entered for values. Please enter again."
            p = enterData()
            #print "\n Inside recursion" #
            return p
    
    # Check to make sure that the minimum is not greater than the maximum
    while (minINum > maxINum):
        print "\n Maximum number of instances must be greater or equal to minimum number. Please enter again."
        while True:
            try:
                mnI = raw_input("\n Enter minimum # of instances: ")
                mxI = raw_input("\n Enter maximum # of instances: ")
                minINum = int(mnI)
                maxINum = int(mxI)
                break
            except ValueError:
                print " Numerical value not entered for values. Please enter again."

    print " Setting values to: \n Minimum Instances: "+mnI+"\n Maximum Instances: "+mxI+"\n Maximum time to wait for instance: "+wT+"\n Maximum time instances can be idle: "+iT+"\n Maximum time instances can be used: "+uT+"\n Isolation mode: "+iM

    return {'minInstances':mnI, 'maxInstances':mxI, 'waitTime':wT, 'idleTime':iT, 'usageTime':uT, 'isolationMode':iM}
    

# A function to generate a token given username, password and the adminURL. - written by Lucas Carrington
def getToken(adminUser, adminPass, server, port, expiration):
    # Build URL
    url = "http://{}:{}/arcgis/admin/generateToken?f=json".format(server, port)
    burl = url.rsplit('/', 1)
    global baseurl
    baseurl = burl[0]+"/services"

    # Encode the query string
    query_dict = {
        'username': adminUser,
        'password': adminPass,
        'expiration': str(expiration),  ## Token timeout in minutes; default is 60 minutes.
        'client': 'requestip'
    }
    query_string = urllib.urlencode(query_dict)

    try:
        # Request the token
        with contextlib.closing(urllib2.urlopen(url, query_string)) as jsonResponse:
            getTokenResult = json.loads(jsonResponse.read())
            ## Validate result
            if "token" not in getTokenResult or getTokenResult == None:
                raise Exception(" Failed to get token: {}".format(getTokenResult['messages']))
            else:
                return getTokenResult['token']

    except urllib2.URLError, e:
        raise Exception(" Could not connect to machine {} on port {}\n{}".format(server, port, e))
        logging.info(' [{0}] : Could not connect to machine: {1} '.format(strftime("%Y-%m-%d %H:%M:%S", localtime()), e))
        return -1

# Lists services on a server - based on listserverServices.py written by Lucas Carrington
def getCatalog(baseUrl, token):
    catalog = json.load(urllib2.urlopen(baseUrl + "/" + "?f=json&token="+token))
    #print "Opened: " + baseUrl + "/" + "?f=json&token="+token
    if "error" in catalog:
        print " Error in gathering services"
        return -1
    rs = catalog['services']  
    try:
        f = catalog['folders']
    except:
        f = []
    return {'services':rs, 'folders':f}  

#Creates a new option list from services
def getServiceOptions(servicelist):
	services = []
	for service in servicelist:
		services.append('%s : %s' % (service['serviceName'], service['type']))
	newOptions = forop.getOptionString(services, True)
	if newOptions == -1:
		print " FUNCTION ERROR"
		return
	return newOptions

# A function that checks that the input JSON object is not an error object. - from ESRI    
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print " Error: JSON object returns an error. " + str(obj)
        return False
    else:
        return True    

# Change the service properties - modified from method written by ESRI
def changeServiceProperties(serverN, serverP, service, type, folder, props, tok):

     # Connect to service to get its current JSON definition    
    httpConn = httplib.HTTPConnection(serverN, serverP)
    params = urllib.urlencode({'token': tok, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    serviceURL = "/arcgis/admin/services/"+folder+"/"+service+"."+type
    httpConn.request("POST", serviceURL, params, headers)

    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print " Could not read service information."
        return 0
    else:
        data = response.read()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):          
            print " Error when reading service information. " + str(data)
            return 0
        else:
            print " Service information for "+service+" read successfully. Now changing properties..."

        # Deserialize response into Python object
        dataObj = json.loads(data)
        httpConn.close()

        # Edit desired properties of the service
        dataObj["minInstancesPerNode"] = props["minInstances"]
        dataObj["maxInstancesPerNode"] = props["maxInstances"]
        dataObj["maxWaitTime"] = props["waitTime"]
        dataObj["maxIdleTime"] = props["idleTime"]
        dataObj["maxUsageTime"] = props["usageTime"]
        dataObj["isolationLevel"] = props["isolationMode"]

        # Serialize back into JSON
        updatedSvcJson = json.dumps(dataObj)

        # Call the edit operation on the service. Pass in modified JSON.
        editSvcURL = "/arcgis/admin/services/"+folder+"/"+service+"."+type+"/edit"
        params = urllib.urlencode({'token': tok, 'f': 'json', 'service': updatedSvcJson})
        httpConn.request("POST", editSvcURL, params, headers)
        
        # Read service edit response
        editResponse = httpConn.getresponse()
        if (editResponse.status != 200):
            httpConn.close()
            print " Error while executing edit."
            return 0
        else:
            editData = editResponse.read()
            
            # Check that data returned is not an error object
            if not assertJsonSuccess(editData):
                print " Error returned while editing "+service +" " + str(editData)
                return 0
            else:
                print " "+service+" edited successfully."
        httpConn.close()  

        return 1  
        
# Script start 
if __name__ == "__main__":
    main()
