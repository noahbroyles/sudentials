# su_dentials
A Python credentials manager that uses pro technology to keep your creds and P-dubs safe.

`su_dentials` is a shitty name, I agree. It's fugly and stupid, but get over it. It basically means 'sudo credentials'.


## How to set up:
First, create the directory `/var/secure` owned by root with `740` permissions.
```console
sudo mkdir /var/secure;sudo chmod 740 /var/secure
```
Next, generate a salt to use for encrypting your credentials.
The salt will be saved as `/var/secure/robocrypt.salt`.
```console
sudo python3 generateSalt.py <good big integer salt length (like 1000)>
```
Next, copy the following file into `/var/secure/creds.json` (you better be root):
```json
{
    "ENV": {
        "ENV_VAR_KEY": "credential value",
        "DBUSER": "yeeyee",
        "DBPASSWD": "haw haw",
        "DATABASE": "dying crow",
        "INNERTUBE_API_KEY": "AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30"
    },
    "GLOBAL": {
        "API_KEY": "yee royal haww",
        "WHAT_EVER_ELSE": "you bally well want"
    }
}
```
***FINALLY***:  
Copy `robocrypt.py` and `su_dentials.py` into your Python installation's `dist-packages`:
```console
sudo cp robocrypt.py su_dentials.py /usr/lib/python3/dist-packages/.
```
Now you're ready to rock and freaking roll! Open up a root terminal session and do this:
```pycon
>>> from su_dentials import Credentials
>>> creds = Credentials()
>>> creds.set_password('something juicy')
>>> creds.lock()
>>>
```
Now remember your password. If you look in `/var/secure`, you will see that `creds.json` has been replaced by `creds.json.robo`, which is an encrypted version of the JSON credentials file you just made.
Your creds are no longer readable by anything other than `su_dentials`, and that only if you have your password.

## The general idea:
Only the root user (we're talking Unix here, not f*cking Windows) will be able to use `su_dentials`, hence the `su` part. That means if you want something to use `su_dentials`, 
you better run that thing as `sudo` or ***it ain't gonna work***. This is by design.  
If you wanna use this in scheduled jobs, chuck em in the `sudo` crontab, and pass the password as a command-line arg.

If you are less security minded, and you just want the shit to work wherever you run it, you can set the perms on `/var/secure` to something less strict, like `777`. You'll still need the main password, which is the only way to decrypt and read your creds.
