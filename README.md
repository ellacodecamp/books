# Instructions

## Preparing for running the script

To run the script you need to install Python 3. So, follow these instructions:

1. In your browser window go to this link [https://www.python.org/ftp/python/3.6.1/python-3.6.1-amd64.exe](https://www.python.org/ftp/python/3.6.1/python-3.6.1-amd64.exe).
1. Wait for download to complete and run downloaded installer. Choose custom installation and click option for all users.
1. Go to GitHub repository [https://github.com/ellacodecamp/books](https://github.com/ellacodecamp/books).
1. Click on "Clone or Download" button and choose "Download ZIP".
1. Extract downloaded ZIP file.
1. Start Windows PowerShell and in there go to the folder that contains this downloaded repository. You command will probably look like ```cd 
C:\something\something```.

Now you should be ready to run the script.

## Running the script

On command prompt in Windows PowerShell windows type the following command

```python .\book_transform.py -h```

This will show you all command line options. The basic use case is just to run this command as follows:

``` python .\book_transform.py <input file name> <output file name>```

To control the number of words per page and minimum number of words on the last page of the chapter, add corresponding command line options.
