日本語の説明は[こちら](http://uzusayuu.hatenablog.com/entry/2018/08/27/091916)をどうぞ。

# What's this?
This is a Python3 script to generate a quiz from English words highlighted in any Kindle book.

To run this, you need
- Windows 64 bit or Python3 execution environment with PyQt5
- html export of highlights from Kindle for PC
- Text file output from Eijiro (English - Japanese Dictionary)
- Anki application (https://apps.ankiweb.net/)

Output is a text file that you can import into Anki

The details of the operation is described in my blog post.
 http://uzusayuu.hatenablog.com/entry/2018/08/27/091916
 
The blog is written in Japanese because this script and the generated quiz are only useful for Japanese speakers.

# How to run
## Binary (Windows 64 bit only)
Download ```dist/vocab_gui.exe``` to Windows-64bit and double click.

## Python script (Python 3 with PyQt5 installed)
Download the repository and run the following inside the folder.

```
$ python vocab_gui.py
```

The usage is explained in the above blog post
