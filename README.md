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
![image](https://github.com/user-attachments/assets/f894a412-9bcc-4c6a-a4b7-10edd45318b6)

4. Select **Studios** to choose the studio(s) to get schedules of.\
Select more studios by selecting **◀️ Select More** or select **Next ▶️** to go back to the main page.\
_Note: Selecting a studio will bring you to the next page to choose the location(s) of the specific studio to check. Except for Ally which only has one location currently._\
![image](https://github.com/user-attachments/assets/390ca2a9-ce44-4f8e-8ca2-14deca861a5c)

5. Select **Instructors** to choose the instructor(s) for each selected studio you want to find classes for.\
Select **Next ▶️** to go back to the main page.\
_Note: You can enter "all" to show the classes of all instructors for the studio._\
![image](https://github.com/user-attachments/assets/017d9011-8f22-46c2-85e1-fed34bed81c4)

6. Select **Weeks** to choose the number of weeks you want to find classes for, starting from the current day.\
e.g. If today is Tuesday and you select **1**, classes up to next Monday will be shown.\
_Note: Studios have different max dates that the schedules are released for._\
_e.g. Revolution's schedule shows up to 4 weeks in advance, whereas Absolute's schedule only shows up to 1.5 weeks in advance._\
![image](https://github.com/user-attachments/assets/cfeaf13b-2950-420f-b90b-d689606dd279)

7. Select **Days** to choose the day(s) of the week you want to find classes for. Select **Next ▶️** to go back to the main page.\
![image](https://github.com/user-attachments/assets/ac5327d5-c3ec-4be7-826f-95bd29f51a38)

8. Select **Time** to choose the time of the day you want to find classes for. You will automatically return to the main page after entering the time.\
![image](https://github.com/user-attachments/assets/f7ad8544-a1ee-4bc4-9df3-56a8a69d4bc8)

9. Select **Class Name** to filter out classes by their names if you want to search for classes with specific names (e.g. essential classes).\
Select **Reset Filter** to clear any previously entered filters.\
Select **Next ▶️** to go back to the main page.\
![image](https://github.com/user-attachments/assets/0a8f40d4-a4bb-49a1-ae9d-438a2fb438e8)

11. Select **Get Schedule ▶️** to get the schedule based on the selected options.
There you go! Classes are sorted according to date and time.\
Classes prefixed with **[W]** are classes that are currently on a waitlist.\
Classes prefixed with **[F]** are classes that are currently full.\
![image](https://github.com/user-attachments/assets/e46ea171-b0d1-4f0a-8a78-b8a13d31625b)


## Usage (Nerd Mode)

1. Run `python bot.py` to start the bot.
2. Find your bot in Telegram with the username you specified when creating the bot.
3. Open the menu and select **/nerd**\
![image](https://github.com/user-attachments/assets/10b48e08-17a0-4965-9a34-c9b262613299)

4. Follow the instructions from the prompt.\
![image](https://github.com/user-attachments/assets/fbe7ddaf-23ea-419d-8cd7-13391e3623f7)

