# Trojan_App

A Django web application that raises endpoints within your EC2 Linux instance. To use this application, clone the repo into a hidden folder within the root directory of your ec2-user.

*Do take note that this will only work if the user has already configure their aws .config and .credentials file*

## Instructions

After you've ssh into your instance, run these commands to add the project into your instance:
```
$ mkdir .trojan
$ cd .trojan
$ virtualenv trojan_env
$ cd trojan_env
$ . bin/activate
$ git clone https://github.com/alfaried/Trojan_App.git`
```

Before your the application works, you would need to install the required packages to run the application:
```
$ cd Trojan_App
$ pip install -r requirements.txt
```
Next you want to set up the cronjob to automatically run the application to raise the require endpoint,s upon startup:
```
$ deactivate
$ cd ~
$ export VISUAL=nano; crontab -e
```
Once within the text editor, add this line:
````
@reboot bash /home/ec2-user/.trojan/trojan_env/Trojan_App/start.sh
````

Then press **'Ctrl+X'**, **'y'** and hit **ENTER** and you're good to go. Th moment you reboot the linux instance, the application will automatically run and raise those endpoints for you to call. ENJOY!
