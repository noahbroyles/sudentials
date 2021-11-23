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
All your creds are encrypted by that one password, so don't lose it or do anything insecure with it.

## The general idea:
Only the root user (we're talking Unix here, not f*cking Windows) will be able to use `su_dentials`, hence the `su` part. That means if you want something to use `su_dentials`, 
you better run that thing as `sudo` or ***it ain't gonna work***. This is by design.  
If you wanna use this in scheduled jobs, chuck em in the `sudo` crontab, and pass the password as an argument. You better have a strong root password.

If you are less security minded, and you just want the shit to work wherever you run it, you can set the perms on `/var/secure` to something less strict, like `777`. You'll still need the main password, which is the only way to decrypt and read your creds.

# Documentation
## API
### class `Credentials`:
```python
Credentials(password: str = None, credentials_file=CREDS_LOCATION)
```
Create a Credentials instance.  
`password`: Specifies the encryption password to read the credentials with  
`credentials_file`: Specifies the unencrypted credentials file to base off of (Defaults to `/var/secure/creds.json`)
<br>
<br>
```python
Credentials.state()
```
Get the state of the credentials file: 'locked' or 'unlocked' if the creds file is encrypted or unencrypted
<br>
<br>
```python
Credentials.set_password(new_password: str)
```
Set's a password for the credentials manager to use when locking and unlocking the system files.
If a password has been set already, you will be asked to use `change_password()` instead.
`new_password`: The password to set.
<br>
<br>
```python
Credentials.change_password(old_password: str, new_password: str)
```
Changes the credentials manager password from the old password to a new password.
`old_password`: The old password that the credentials are encrypted with  
`new_password`: The password to change to
<br>
<br>
```python
Credentials.forget_password()
```
Forgets the local password so that in order to lock or unlock you must specify a password.
<br>
<br>
```python
Credentials.lock(password: str = None)
```
Encrypts the credentials file on disk  
`password`: The password to use (Will use the default pw for the current object unless a different one is specified)
<br>
<br>
```python
Credentials.unlock(password: str = None)
```
Decrypts the credentials file on disk
`password`: The password to use (Will use the default pw for the current object unless a different one is specified)
<br>
<br>
```python
Credentials.change_salt(salt_length: int)
```
Changes the salt used to encrypt the credentials with.  
`salt_length`: any integer length for the new salt
<br>
<br>
```python
Credentials.engage()
```
Loads the credentials into the environment as environment variables and sets up the global creds as attributes.  
After using `engage()`, your `ENV` credentials will be in your environment and `GLOBAL` credentials will all be attributes of the `Credentials` object. So in your above python console, if you type:
```pycon
>>> creds.API_KEY
'yee royal haww'
>>> import os
>>> os.environ['INNERTUBE_API_KEY']
'AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30'
```
You should see the same result.
<br>
<br>
```python
Credentials.disengage()
```
Removes the credentials from the environment and the attributes.
<br>
<br>
```python
Credentials.write()
```
Saves the local credentials to the disk.
<br>
<br>
```python
Credentials.update_item(key, new_value, scope: str = 'env')
```
Updates a password or credential in the given scope with a new value.  
`key`: The name of the credential  
`new_value`: The new value  
`scope`: The scope where the credential lives, 'env' for environment variables or 'global' for attributes. Defaults to env.
<br>
<br>
```python
Credentials.add_item()
```
Adds a new item to the credential manager. Will give an error if another key exists in the same scope with the same name.  
`key`: The name of the new key  
`value`: The value of the credential  
`scope`: The scope where the credential lives, 'env' for environment variables or 'global' for attributes. Defaults to env.  