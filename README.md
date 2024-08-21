# Exercise Studio Telegram Booking Bot

## Overview

My wife and I found ourselves with a handful of exercise packages across various studios and it was getting troublesome trying to find classes we wanted to go for. That was how this idea was born - to create a telegram bot containing the schedules of all the studios we go to!

## Studios Supported

- Absolute
- Ally
- Barry's
- Revolution

## Prerequisites

To be able to run the bot, you will need to get a **bot token**. FreeCodeCamp has a nice guide [here](https://www.freecodecamp.org/news/how-to-create-a-telegram-bot-using-python/) that was used as a reference for this project.

## Usage (Normal Mode)

The main entry point for the bot can be found in the **bot.py** script.

1. Run `python bot.py` to start the bot.
2. Find your bot in Telegram with the username you specified when creating the bot.
3. Open the menu and select **/start** to open up the main page to check the schedule.\
![image](https://github.com/user-attachments/assets/78583297-6a54-4a08-a57f-b406d9d0a88c)
![image](https://github.com/user-attachments/assets/a3c9f65e-16c5-48ac-9c51-ab50e564b899)
4. Select "Studios" to choose the studio(s) to get schedules of.\
Select more studios by selecting **◀️ Select More** or select **Next ▶️** to go back to the main page.\
_Note: Selecting a studio will bring you to the next page to choose the location(s) of the specific studio to check. Except for Ally which only has one location currently._\
![image](https://github.com/user-attachments/assets/470aaeca-3e36-4bdf-a309-7ac50db75879)
5. Select "Instructors" to choose the instructor(s) for each selected studio you want to find classes for.\
Select **Next ▶️** to go back to the main page.\
_Note: You can enter "all" to show the classes of all instructors for the studio._\
![image](https://github.com/user-attachments/assets/4a5d41dc-03f8-4368-ad53-68f49d81ea0b)
6. Select "Weeks" to choose the number of weeks you want to find classes for, starting from the current day.\
e.g. If today is Tuesday and you select "1", classes up to next Monday will be shown.\
_Note: Studios have different max dates that the schedules are released for._\
_e.g. Revolution's schedule shows up to 4 weeks in advance, whereas Absolute's schedule only shows up to 1.5 weeks in advance._\
![image](https://github.com/user-attachments/assets/c5a7a6a6-1309-42b4-82df-e424f869903c)
7. Select "Days" to choose the day(s) of the week you want to find classes for. Select **Next ▶️** to go back to the main page.\
![image](https://github.com/user-attachments/assets/7f1246bf-d308-435b-96c7-1db4d9086107)
8. Select "Get Schedule ▶️" to get the schedule based on the selected options.
There you go! Classes are sorted according to date and time.\
Classes prefixed with **[W]** are classes that are currently on a waitlist.\
Classes prefixed with **[F]** are classes that are currently full.\
![image](https://github.com/user-attachments/assets/d09b0f50-5441-45ec-898f-0952667c31d0)

## Usage (Nerd Mode)

1. Run `python bot.py` to start the bot.
2. Find your bot in Telegram with the username you specified when creating the bot.
3. Open the menu and select **/nerd**\
![image](https://github.com/user-attachments/assets/d264dbfb-e88b-4505-93eb-5e05ec070fbe)
4. Follow the instructions from the prompt.\
![image](https://github.com/user-attachments/assets/676c03b9-a407-4aed-a581-4e4a5ec0b08c)
