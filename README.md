# ChatGPT Account Auto Register

## Introduction

With the python script, you can easily register ChatGPT official accounts. 

**This project is for educational purposes exculsively.**

## Installation & Usage

It is suggested to run the script on Windows - it seemed not to be working on my Ubuntu desktop. 

First, ensure that Chrome and Python 3 are installed on your computer. Then clone the repo, and the command

```
pip install -r requirements.txt
```

will help install all packages required.

You also need to acquire an API key on sms-activate.com, the website that helps receive SMS verification code from OpenAI. Once you get the key, replace `'YOUR-API-KEY'` with it in the 99 column of `register.py`.

Good network environment is also required, especially if you live in OpenAI's unsupported regions, including Chinese mainland and Hong Kong, etc. 

With everything prepared, run the script with
```
python3 register.py
```

If everything goes well, the program will automatically complete the whole registration procedure (including creating a temperoray email, signing up on openai.com, gaining a virtual phone number and creating an OpenAI API key). If it gets stuck somewhere, you may manually click some button or finish some CAPTCHA on the webpage, and the process will continue. 
