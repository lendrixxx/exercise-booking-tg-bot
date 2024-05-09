# Overview
My wife and I found ourselves with a handful of exercise packages across various studios and it was getting troublesome trying to find classes we wanted to go for. That was how this idea was born - to create a telegram bot containing the schedules of all the studios we go to! <br/>

# Studios Supported
- Revolution
- Barry's
- Absolute

We also bought an ALLY package recently, so that will probably be added next...

# Prerequisites
To be able to run the bot, you will need to get a **bot token**. FreeCodeCamp has a nice guide [here](https://www.freecodecamp.org/news/how-to-create-a-telegram-bot-using-python/) that was used as a reference for this project.

# Usage
The main entry point for the bot can be found in the **bot.py** script. <br/>

1. Run `python bot.py` to start the bot. <br/>
2. Find your bot in Telegram with the username you specified when creating the bot. <br/>
3. Open the menu and select **/start** and follow the instructions to select the studio(s)/instructor(s)/day(s) that you would like to check the schedule for. <br/>
![image](https://github.com/XirdneL/exercise-booking-tg-bot/assets/65599524/87d66f9b-9c06-4e26-96f5-c48ab9045232)
![image](https://github.com/XirdneL/exercise-booking-tg-bot/assets/65599524/5ab96f18-1dbb-4071-930e-b8d5db56f2b2)
4. Select the studio(s) to view schedules of. Once done, you can select more studios by selecting **◀️ Select More**<br/>
or select **Next ▶️** to proceed to the next step. <br/>
_Note: Selecting a studio will bring you to the next page to choose the location(s) of the specific studio to check._ <br/>
![image](https://github.com/XirdneL/exercise-booking-tg-bot/assets/65599524/2272e7e3-19c1-4803-a5ff-98391f6ba311)
5. Enter the names of the instructor(s) you want to find classes for. Select **Next ▶️** to proceed to the next step. <br/>
_Note: You can enter "all" to show the classes of all instructors for the studio. <br/>_
![image](https://github.com/XirdneL/exercise-booking-tg-bot/assets/65599524/3c0567d7-a648-4609-8094-576a7f21a1a5)
6. Select the number of weeks you want to find classes for, starting from the current day. <br/>
e.g. If today is Tuesday and you select "1", classes up to next Monday will be shown. <br/>
_Note: Studios have different max dates that the schedules are released for._ <br/>
_e.g. Revolution's schedule shows up to 4 weeks in advance, whereas Absolute's schedule only shows up to 1.5 weeks in advance._ <br/>
![image](https://github.com/XirdneL/exercise-booking-tg-bot/assets/65599524/f7685daa-3e0e-48a4-a329-c0cea283b8c3)
7. Select the day(s) of the week you want to find classes for. Select **Next ▶️** to proceed to the next step. <br/>
![image](https://github.com/XirdneL/exercise-booking-tg-bot/assets/65599524/8b7d43a2-d98e-4e57-8538-9a29a5858f16)
![image](https://github.com/XirdneL/exercise-booking-tg-bot/assets/65599524/e4db223b-c1eb-4771-a46e-769003548664)
8. There you go! Classes are sorted according to date and time. <br/>
Classes prefixed with **[W]** are classes that are currently on a waitlist. <br/>
Classes prefixed with **[F]** are classes that are currently full. <br/>
![image](https://github.com/XirdneL/exercise-booking-tg-bot/assets/65599524/d8f3ff2a-c3f7-4426-997f-8fda1d43ce0f)


