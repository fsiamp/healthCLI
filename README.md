# healthCLI
Health Measurement and Notification CLI

<b>User Authentication and Application Authorization</b>

1.End user requests an oAuth token and creates authorization request through CLI (consumer key and consumer secret are already known by CLI since application has already been registered in Nokia Health).
2.OAuth Service returns back to CLI a URL which the end user will use in order to manually get access (e.ghttps://developer.health.nokia.com/account/authorize?oauth_token=826d1d367d6756f51bc6e81471cd094ccbf47c7282edc4def1dc7696cb923)
3.User opens up the URL in a browser and logins with his Nokia Health credentials. After, he is asked if he wants to grant access to this application for reading data and profile.
4.End user allows the partner to access the data.

5.Once access is granted oAuth token and oAuth verifier are displayed (e.g oauth_token=826d1d367d6756f51bc6e81471cF094ccbf47c7282edc4def1dc7696cb923&oauth_verifier=WpR1ooKRtJF)
6.End user copies oAuth verifier into CLI.

<b>CLI Command Format</b>:

Some of the following commands are planned to be used on CLI.

Authentication

1.<b>authorize</b>

Sample Output:
https://developer.health.nokia.com/account/authorize?oauth_token=826d1d367d6756f51bc6e81471cd094ccbf47c7282edc4def1dc7696cb923

2.<b>set <oAuth_verifier></b>

Sample Output:
User ID: 13584569

<b>Measurements</b>

Once authentication has been established successfully, now user is able to make use of Nokia Health APIs. For displaying measurement data the comman

1.<b>workouts <start_date> <end_date></b>: retrieve all the details for each workout happening during this timeframe.

Sample Output:

Category: Table Tennis
Timezone: Europe/Athens
Way of Measure Attribution: 2
Model: 54
Date: 2017-10-06
Distance: 0
Elevation: 0
Minimum Heart Rate: 0
Average Heart Rate: 0
Calories: 866
Intensity: 30
Steps: 0
Heart Rate Zone 0: 0
Heart Rate Zone 1: 0
Heart Rate Zone 2: 0
Heart Rate Zone 3: 0
Effective Duration: 8400
Maximum Heart Rate: 0

2.<b>activity <start_date> <end_date></b>: Returns activity-related data

Sample Output:

Distance: 4517.99
Elevation: 0
Calories: 191.66
Steps: 5278
Total Calories: 1996.402
Date: 2017-09-18
Timezone: Europe/Athens
Soft: 9000
Intense: 0

3.<b>sleep summary <start_date> <end_date></b>: Displays sleep summary details (duration, wakeup counts etc)

Sample Output:

Sleep Id: 638758136
Timezone: Europe/Athens
Date: 2017-09-12
Wakeup Duration: 0
Deep Sleep Duration: 7020
Light Sleep Duration: 0
Sleep Duration: 0
Wakeup Count: 0

4.<b>sleep measures <start_date> <end_date></b>: Displays brief sleep states and models.

Sample Output:
Model: Aura

Start Date: 2017-06-24
End Date: 2017-06-24
State: REM

Start Date: 2017-06-24
End Date: 2017-06-24
State: Deep

Start Date: 2017-06-24
End Date: 2017-06-24
State: Light

5.<b>body <start_date> <end_date></b>: Returns output that includes data regarding body measures during the defined timeframe

Sample Output:

Timezone: Europe/Athens
Update Time: 1507492677

Calories: 1506970850
Category: 1
Way of Measure Attribution: 2
Measure Group ID: 918719142
Measure Type: 1
Measure Value: 91000
Measure Unit: -3

Calories: 1495033327
Category: 1
Way of Measure Attribution: 2
Measure Group ID: 800387319
Measure Type: 4
Measure Value: 193
Measure Unit: -2

6.<b>search tabletennis <start_date> <end_date></b>: Returns queries for table tennis workouts during the defined timeframe
     
Sample Output:

Category: Table Tennis
Timezone: Europe/Athens
Way of Measure Attribution: 2
Model: 54
Date: 2017-10-06
Distance: 0
Elevation: 0
Minimum Heart Rate: 0
Average Heart Rate: 0
Calories: 866
Intensity: 30
Steps: 0
Heart Rate Zone 0: 0
Heart Rate Zone 1: 0
Heart Rate Zone 2: 0
Heart Rate Zone 3: 0
Effective Duration: 8400
Maximum Heart Rate: 0

7.<b>intraday <date></b>: Returns activity measures for a specific day
     
Sample Output:

Distance: 4251.609
Elevation: 0
Calories: 180.402
Steps: 4964
Total Calories: 1982.092
Date: 2017-09-07
Timezone: Europe/Athens
Soft: 9120
Intense: 0

<b>Notifications</b>

End user’s system is able to be notified when new data is available for another user (for example when he syncs device, modifies data etc). A reachable callback URL is used for notifying end user.

1.<b>notify <callback_url> <user_id> <measure_type> <comment></b>: Creates a new notification by specifying the callback URL, the targeted user id of about whom we would like to be notified, measure type and a comment that will be used as a description of our notification setup.

2.<b>list <measure_type></b>: Displays all existing notifications for this measure type (sleep, heart rate, activity or weight)

Sample Output:

Callback URL: http://nokia.com
Comment: multiple test

Callback URL: http://nokia.fi
Comment: test measure

3.<b>revoke <callback_url> <measure_type></b>: Deletes notification that uses the specific callback URL and measure type

4.<b>show <callback_url> <measure_type></b>: Displays notification information

Sample Output:

Callback URL: http://nokia.com
Comment: multiple test
Expires: 2147483647
Measure Type: 16


Finally, logging procedure will be possible through `export` command which will save all REST responses during a specific user session in a new file inside application’s directory.
