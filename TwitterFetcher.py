from birdy.twitter import UserClient, BirdyException 
from time import sleep
import string
import argparse

key = [
    ["Consumer Key", "Consumer Secret", "Access Token", "Access Token Secret"]
]

client = UserClient(key[0][0], key[0][1], key[0][2], key[0][3])

def user_show(client, key, uid, sname, info):
	'''
	https://dev.twitter.com/rest/reference/get/users/show

	Returns a variety of information about the user specified by the required user_id or screen_name parameter.

	1. You need to enter your API credentials to the key list.
	2. You can specify which info you need to the info list. You can find the name of the returned parameters (id, followers_count etc.) in the link above.
	3. Script outputs the resulting data to user_show_out.txt as a csv formatted file
	'''

	userInfo = []

	try:
		response = client.api.users.show.get(user_id=uid, screen_name = sname)
		tmpInfo = []
		for i in info:
			tmpInfo.append(response.data[i])
		userInfo.append(tmpInfo)
		print(userInfo)
	except Exception as err:
		print(err.status_code)
		print(err)

	filename = 'user_show_out.txt'
	f = open(filename, 'w', encoding='utf-8')

	f.write(str(info[0]))
	for i in info[1:]:
		f.write(',')
		f.write(str(i))
	f.write("\n")

	for ui in userInfo:
		f.write(str(ui[0]))
		for i in ui[1:]:
			f.write(',')
			f.write(str(i))
		f.write("\n")
	f.close()


def user_lookup(client, key, delim='\n'):
	'''
	https://dev.twitter.com/rest/reference/get/users/lookup

	Script takes list of user_id s and returns the specified information for each user. Script reads user_id s from "user_lookup_in.txt".
	Before running the script specify your delimeter: ',' (comma), ' ' (space) or '\n' (new line) as default.

	user_show is used to retrieve a single user object.

	There are a few things to note when using this method:

	* You must be following a protected user to be able to see their most recent status update. If you don’t follow a protected user their status will be removed.
	* The order of user IDs or screen names may not match the order of users in the returned array.
	* If a requested user is unknown, suspended, or deleted, then that user will not be returned in the results list.
	* If none of your lookup criteria can be satisfied by returning a user object, a HTTP 404 will be thrown.

	1. You need to enter your API credentials to the key list.
	2. You can specify which info you need to the info list. You can find the name of the returned parameters (id, followers_count etc.) in the link above.
	3. Script outputs the resulting data to user_lookup_out.txt as a csv formatted file
	'''

	f = open('user_lookup_in.txt', 'r', encoding='utf-8')
	userIDs = f.read().split(delim)
	f.close()
	    
	print('Number of user IDs: ' + str(len(userIDs)))


	userInfo = []

	for i in range(int(len(userIDs)/100)+1):
	    imin = i*100
	    imax = (i+1)*100
	    if i == int(len(userIDs)/100):
	        imax = len(userIDs)
	    while(True):
	        try:
	            response = client.api.users.lookup.get(user_id=userIDs[imin : imax])
	            for rd in response.data:
	                tmpInfo = []
	                for i in info:
	                    tmpInfo.append(rd[i])
	                userInfo.append(tmpInfo)
	            break
	        except Exception as err:
	            print(err.status_code)
	            print(err)
	            if err.status_code == 429:
	                sleep(60)
	                keyInd = (keyInd + 1)%len(key)
	            else:
	                break
	            client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])

	filename = 'user_lookup_out.txt'
	f = open(filename, 'w', encoding='utf-8')

	f.write(str(info[0]))
	for i in info[1:]:
	    f.write(',')
	    f.write(str(i))
	f.write("\n")

	for ui in userInfo:
	    f.write(str(ui[0]))
	    for i in ui[1:]:
	        f.write(',')
	        f.write(str(i))
	    f.write("\n")
	f.close()


def users_tweets(client, key, delim='\n'):
	'''
	https://dev.twitter.com/rest/reference/get/statuses/user_timeline

	Returns a collection of the most recent Tweets posted by the users indicated by their user_id parameters.

	1. You need to enter your API credentials to the key list.
	2. Script takes list of user_id s and returns the specified information for each user. Script reads user_id s from "user_ids.txt".
	   Before running the script specify your delimeter: ',' (comma), ' ' (space) or '\n' (new line) as default.
	3. Script outputs each user's tweets in a different file named as "Tweets/USER-ID.txt". So first you should create a folder named 'Tweets'.
	4. Also script writes how many tweets has been fetched from a user to "Tweets/tweetCounter.txt"
	'''

	f = open('user_ids.txt', 'r', encoding='utf-8')
	userIDs = f.read().split(delim)
	f.close()

	print('Number of user IDs: ' + str(len(userIDs)))


	i = 0
	for user in userIDs:
	    tweetCTR = 0
	    filename = "Tweets/" + user + ".txt"
	    f = open(filename, 'w', encoding='utf-8')
	    
	    print(str(i) + '. ' + str(user))
	    protec = False
	    twe = []
	    
	    while(True):
	        try:
	            response = client.api.statuses.user_timeline.get(user_id=user, count=200)
	            break
	        except Exception as err:
	            print(err.status_code)
	            print(err)
	            if err.status_code == 429:
	                sleep(60)
	                keyInd = (keyInd + 1)%len(key)
	            else:
	                protec = True
	                break
	            
	            client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])
	            
	    if protec or len(response.data) == 0:
	        print('protected!')
	        f.close()
	        continue
	        
	    tweetCTR += len(response.data)
	    for d in response.data:
	        twe.append(d['text'])
	        f.write(d['text'])
	        f.write(" ")
	        
	    maxID = response.data[-1]['id']
	    
	    while(maxID != 0):
	        while(True):
	            try:
	                response = client.api.statuses.user_timeline.get(user_id=user, count=200, max_id = maxID-1)
	                break
	            except Exception as err:
	                print(err.status_code)
	                print(err)
	                if err.status_code == 429:
	                    sleep(60)
	                    keyInd = (keyInd + 1)%len(key)
	                else:
	                    sleep(15)
	                client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])
	        
	        if len(response.data) == 0:
	            break
	        
	        tweetCTR += len(response.data)
	        for d in response.data:
	            twe.append(d['text'])
	            f.write(d['text'])
	            f.write(" ")
	            
	        maxID = response.data[-1]['id']
	            
	    f.close()
	    f = open("Tweets/tweetCounter.txt", 'a', encoding='utf-8')
	    f.write(user + "," + str(tweetCTR) + "\n")
	    f.close()
	    i += 1

def followers_ids(client, key, uid, sname):
	'''
	https://dev.twitter.com/rest/reference/get/followers/ids

	Returns ids of the followers of a user specified by the required user_id or screen_name parameter.

	1. You need to enter your API credentials to the key list.
	2. Script outputs the resulting data to followers_ids_out.txt as a csv formatted file
	'''

	followerIDs = []

	protec = False

	while(True):
	    try:
	        response = client.api.followers.ids.get(user_id = uid, screen_name = sname, count=5000, cursor=-1)
	        break
	    except Exception as err:
	        print(err.status_code)
	        print(err)
	        if err.status_code == 429:
	            sleep(60)
	            keyInd = (keyInd + 1)%len(key)
	        else:
	            protec = True
	            break
	        client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])
	        
	if protec:
	    followerIDs.append([])
	    print('protected!')
	else:
	    ncur = response.data['next_cursor']
	    for s in response.data['ids']:
	        followerIDs.append(s)

	    while(ncur != 0):
	        while(True):
	            try:
	                response = client.api.followers.ids.get(user_id = uid, screen_name = sname, count=5000, cursor=ncur)
	                break
	            except Exception as err:
	                print(err.status_code)
	                print(err)
	                if err.status_code == 429:
	                    sleep(60)
	                    keyInd = (keyInd + 1)%len(key)
	                else:
	                    sleep(15)
	                client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])

	        ncur = response.data['next_cursor']
	        for s in response.data['ids']:
	            followerIDs.append(s)

	filename = 'followers_ids_out.txt'
	f = open(filename, 'w', encoding='utf-8')

	f.write(str(followerIDs[0]))
	for ids in followerIDs[1:]:
	    f.write(',')
	    f.write(str(ids))

	f.close()

def followers_info(client, key, uid, sname, info):
	'''
	https://dev.twitter.com/rest/reference/get/followers/ids

	Returns variety of information of the followers of a user specified by the required user_id or screen_name parameter.

	1. You need to enter your API credentials to the key list.
	2. Enter the user_id or screen_name ofthe user whoose followers will be fetched.
	3. You can specify which info you need to the info list. You can find the name of the returned parameters (id, followers_count etc.) in the link above.
	4. Script outputs the resulting data to followers_info_out.txt as a csv formatted file
	'''

	followerIDs = []

	protec = False

	while(True):
	    try:
	        response = client.api.followers.ids.get(user_id = uid, screen_name = sname, count=5000, cursor=-1, stringify_ids=True)
	        break
	    except Exception as err:
	        print(err.status_code)
	        print(err)
	        if err.status_code == 429:
	            sleep(60)
	            keyInd = (keyInd + 1)%len(key)
	        else:
	            protec = True
	            break
	        client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])
	        
	if protec:
	    followerIDs.append([])
	    print('protected!')
	else:
	    ncur = response.data['next_cursor']
	    for s in response.data['ids']:
	        followerIDs.append(s)

	    while(ncur != 0):
	        while(True):
	            try:
	                response = client.api.followers.ids.get(user_id = uid, screen_name = sname, count=5000, cursor=ncur, stringify_ids=True)
	                break
	            except Exception as err:
	                print(err.status_code)
	                print(err)
	                if err.status_code == 429:
	                    sleep(60)
	                    keyInd = (keyInd + 1)%len(key)
	                else:
	                    sleep(15)
	                client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])

	        ncur = response.data['next_cursor']
	        for s in response.data['ids']:
	            followerIDs.append(s)

	userInfo = []

	for i in range(int(len(followerIDs)/100)+1):
	    imin = i*100
	    imax = (i+1)*100
	    if i == int(len(followerIDs)/100):
	        imax = len(followerIDs)
	    while(True):
	        try:
	            response = client.api.users.lookup.get(user_id=followerIDs[imin : imax])
	            for rd in response.data:
	                tmpInfo = []
	                for i in info:
	                    tmpInfo.append(rd[i])
	                userInfo.append(tmpInfo)
	            break
	        except Exception as err:
	            print(err.status_code)
	            print(err)
	            if err.status_code == 429:
	                sleep(60)
	                keyInd = (keyInd + 1)%len(key)
	            else:
	                break
	            client = UserClient(key[keyInd][0], key[keyInd][1], key[keyInd][2], key[keyInd][3])


	filename = 'followers_info_out.txt'
	f = open(filename, 'w', encoding='utf-8')

	f.write(str(info[0]))
	for i in info[1:]:
	    f.write(',')
	    f.write(str(i))
	f.write("\n")

	for ui in userInfo:
	    f.write(str(ui[0]))
	    for i in ui[1:]:
	        f.write(',')
	        f.write(str(i))
	    f.write("\n")
	f.close()


parser = argparse.ArgumentParser(description='Twitter Fetcher')

parser.add_argument('process', type=int,
                    help = '1: user_show, 2: user_lookup, 3: users_tweets, 4: followers_ids, 5: followers_info')
parser.add_argument('--sname', type=str,
                    help='Screen Name of user (for 1, 4, 5)')
parser.add_argument('--uid', type=int,
                    help='User ID of user (for 1, 4, 5)')
parser.add_argument('--info', type=str, nargs="+",
                    help='Which information of users to collect (for 1, 2, 5)')
parser.add_argument('--delim', type=str, nargs="+",
                    help="Type of delimeter: ',' (comma), ' ' (space) or (new line) as default (for 2, 3)")

args = parser.parse_args()

uid = args.uid
sname = args.sname
info = args.info
delim = args.delim

if args.process == 1:
	if uid == None and sname == None:
		print('\n!!! You should enter User ID or Screen Name !!!!\n')
		parser.parse_args(['-h'])
	elif info == None:
		print('\n!!! Info is missing !!!!\n')
		parser.parse_args(['-h'])
	else:
		user_show(client, key, uid, sname, info)
elif args.process == 2:
	user_lookup(client, key, delim)
elif args.process == 3:
	users_tweets(client, key, delim)
elif args.process == 4:
	if uid == None and sname == None:
		print('\n!!! You should enter User ID or Screen Name !!!!\n')
		parser.parse_args(['-h'])
	else:
		followers_ids(client, key, uid, sname)
elif args.process == 5:
	if uid == None and sname == None:
		print('\n!!! You should enter User ID or Screen Name !!!!\n')
		parser.parse_args(['-h'])
	elif info == None:
		print('\n!!! Info is missing !!!!\n')
		parser.parse_args(['-h'])
	else:
		followers_info(client, key, uid, sname, info)
else:
	parser.parse_args(['-h'])
