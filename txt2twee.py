# python3

import argparse
from html.parser import HTMLParser
from enum import Enum, auto
import re

parser = argparse.ArgumentParser(description = "This program converts a normal book txt file into paginated twee file.")
parser.add_argument("input-file", help = "Input '.txt' file", type = argparse.FileType(mode = 'r', encoding = 'utf-8'))
parser.add_argument("output-file", help = "Output '.twee' file", type = argparse.FileType(mode = 'w', encoding = 'utf-8-sig'))
parser.add_argument("-wc", "--word-count", nargs = "?", help = "Number of words per page (default: %(default)s).", type = int, default = 300)
parser.add_argument("-mwl", "--min-words-last-page", nargs = "?", help = "Minimum number of words on the last page of a chapter (default: %(default)s).",
                    type = int, default = 100)
parser.add_argument("-hd", "--heading", nargs = "?", help = "Heading tag to be used for chapter identification (default: %(default)s).", type = str,
                    default = "h1", choices = ["h1", "h2", "h3", "h4", "h5", "h6"])

args = parser.parse_args()

# print(vars(args))

input_file = vars(args)["input-file"]
output_file = vars(args)["output-file"]

# write header
header = [
  ":: Start\n",
  "Your story will display this passage first. Edit it by double clicking it.\n\n\n",
  ":: StoryTitle\n",
  "Untitled Story\n\n\n",
  ":: StoryAuthor\n",
  "Anonymous\n\n\n",
  ":: Summary\n"
]
output_file.writelines(header)


class ParseState(Enum):
  START = auto()
  BEFORE_HEADING = auto()
  HEADING = auto()
  FIRST_PAGE = auto()
  NEXT_PAGE = auto()
  END = auto()


class MyHTMLParser(HTMLParser):
  # I do not really need that, but PyCharm insisted I do
  def error(self, message):
    pass

  def __init__(self):
    HTMLParser.__init__(self, convert_charrefs = False)
    self.parse_state = ParseState.START
    self.div_level = 0
    self.current_word_count = 0
    self.prev_word_count = 0
    self.current_page = str()
    self.prev_page = str()
    self.chapter = str()
    self.page_full = False
    self.major_number = int(0)
    self.minor_number = int(0)
    self.prev_label = str("Start")
    self.current_label = str()
    self.next_label = str()

  def add_current_page(self, data, wc):
    self.current_page += data
    if wc != 0:
      self.current_word_count += wc
      if self.current_word_count > args.word_count:
        self.page_full = True
      if self.prev_word_count != 0 and self.current_word_count > args.min_words_last_page and self.parse_state == ParseState.NEXT_PAGE:
        self.chapter += self.prev_page
        self.prev_page = str()
        self.prev_word_count = 0
        self.minor_number += 1
        next_label = str(self.major_number) + "." + str(self.minor_number)
        page_footer = [
          '\n<p style="text-align:left;">[[<<<|' + self.prev_label + ']]<span style="float:right;">[[>>>|' + next_label + ']]</span></p><br /><br />\n',
          '\n', '\n', '\n', '\n',
          ":: " + next_label + "\n"
        ]
        self.chapter += "".join(page_footer)
        self.prev_label = self.current_label
        self.current_label = next_label

  def publish_chapter(self):
    if self.prev_word_count != 0:
      self.chapter += self.prev_page
      self.prev_page = str()
      self.prev_word_count = 0
    self.chapter += self.current_page
    self.current_page = str()
    self.current_word_count = 0
    output_file.write(self.chapter)
    self.chapter = str()

  def validate_start_state(self, message):
    if self.parse_state == ParseState.START:
      raise Exception(message + " in start state!")

  def validate_end_state(self, message):
    if self.parse_state == ParseState.END:
      raise Exception(message + " after end!")

  def validate_processing_state(self, message):
    if self.parse_state != ParseState.BEFORE_HEADING and self.parse_state != ParseState.HEADING and self.parse_state != ParseState.FIRST_PAGE and \
        self.parse_state != ParseState.NEXT_PAGE:
      raise Exception(message + " in invalid state!")

  def validate_all_states(self, message):
    if self.parse_state != ParseState.START and self.parse_state != ParseState.BEFORE_HEADING and self.parse_state != ParseState.HEADING and \
            self.parse_state != ParseState.FIRST_PAGE and self.parse_state != ParseState.NEXT_PAGE and self.parse_state != ParseState.END:
      raise Exception(message + " in invalid state '" + str(self.parse_state) + "'!")

  def validate_state(self, message):
    self.validate_start_state(message)
    self.validate_end_state(message)
    self.validate_processing_state(message)

  @staticmethod
  def validate(condition, message):
    if condition:
      Exception(message)

  def handle_starttag(self, tag, attrs):
    # print("Encountered a start tag: ", self.get_starttag_text())
    self.validate_end_state("Unexpected tag '" + self.get_starttag_text() + "'")
    self.validate(self.parse_state == ParseState.HEADING and tag == args.heading, "Unexpected tag '" + self.get_starttag_text() + "' inside heading!")

    if self.parse_state == ParseState.START:
      if tag == "div":
        output_file.write(self.get_starttag_text())
        self.parse_state = ParseState.BEFORE_HEADING
        self.div_level += 1
      else:
        raise Exception("Unexpected begin tag '" + self.get_starttag_text() + "'!")
    else:
      if tag == "div":
        self.div_level += 1
      elif tag == args.heading:
        self.major_number += 1
        self.minor_number = 0
        saved_current_label = self.current_label
        self.current_label = str(self.major_number) + "." + str(self.minor_number)
        chapter_header = [
          '\n<p style="text-align:left;">[[<<<|' + self.prev_label + ']]<span style="float:right;">[[>>>|' + self.current_label + ']]</span></p><br /><br />\n',
          '\n', '\n', '\n', '\n',
          ":: " + self.current_label + "\n"
        ]
        if self.parse_state == ParseState.BEFORE_HEADING:
          # if major_number == 1:
          self.prev_label = str("Summary")
          output_file.writelines(chapter_header)
        else:
          self.add_current_page("".join(chapter_header), 0)
          self.publish_chapter()
          if self.parse_state == ParseState.FIRST_PAGE or self.parse_state == ParseState.NEXT_PAGE:
            self.prev_label = saved_current_label
          else:
            raise Exception("Unexpected state for heading!")
        # output_file.writelines(chapter_header)
        self.parse_state = ParseState.HEADING
      if self.parse_state == ParseState.BEFORE_HEADING:
        output_file.write(self.get_starttag_text())
      elif self.parse_state == ParseState.HEADING or self.parse_state == ParseState.FIRST_PAGE or self.parse_state == ParseState.NEXT_PAGE:
        self.add_current_page(self.get_starttag_text(), 0)
      else:
        raise Exception("Unexpected state for tag '" + self.get_starttag_text() + "'!")

  def handle_endtag(self, tag):
    self.validate_state("Unexpected end of tag '" + tag + "'")

    if tag == 'div':
      self.validate(self.div_level == 0, "Invalid div level found!")
      self.div_level -= 1
      if self.div_level == 0:
        self.parse_state = ParseState.END

    if self.parse_state == ParseState.BEFORE_HEADING:
      output_file.write("</" + tag + ">")
    elif self.parse_state == ParseState.HEADING or self.parse_state == ParseState.FIRST_PAGE or self.parse_state == ParseState.NEXT_PAGE:
      if self.parse_state == ParseState.HEADING and tag == args.heading:
        self.parse_state = ParseState.FIRST_PAGE
      self.add_current_page("</" + tag + ">", 0)
    elif self.parse_state == ParseState.END:
      chapter_footer = [
        '\n<p style="text-align:left;">[[<<<|' + self.prev_label + ']]<span style="float:right;">[[>>>|EndShare]]</span></p><br /><br />\n',
        '\n', '\n', '\n', '\n'
      ]
      self.add_current_page("".join(chapter_footer), 0)
      self.publish_chapter()
      output_file.write("</" + tag + ">")

  def handle_startendtag(self, tag, attrs):
    self.validate_state("Unexpected tag '" + self.get_starttag_text() + "'")

    if self.parse_state == ParseState.BEFORE_HEADING:
      output_file.write(self.get_starttag_text())
    elif self.parse_state == ParseState.HEADING:
      self.add_current_page(self.get_starttag_text(), 0)
    elif self.parse_state == ParseState.FIRST_PAGE or self.parse_state == ParseState.NEXT_PAGE:
      self.add_current_page(self.get_starttag_text(), 0)
      if tag == "br" and self.page_full:
        self.prev_page = self.current_page
        self.current_page = str()
        self.prev_word_count = self.current_word_count
        self.current_word_count = 0
        self.parse_state = ParseState.NEXT_PAGE
        self.page_full = False

  def handle_data(self, data):
    self.validate_all_states("Unexpected data '" + data + "'")

    if self.parse_state == ParseState.BEFORE_HEADING:
      output_file.write(data)
    elif self.parse_state == ParseState.HEADING:
      self.add_current_page(data, 0)
    elif self.parse_state == ParseState.FIRST_PAGE or self.parse_state == ParseState.NEXT_PAGE:
      words = re.findall(r'\S+', data)
      self.add_current_page(data, len(words))

  def handle_charref(self, name):
    print("Encountered charref :", name)

  def handle_entityref(self, name):
    self.validate_all_states("Unexpected entityref '" + name + "'")
    entity = "&" + name + ";"
    if self.parse_state == ParseState.BEFORE_HEADING:
      output_file.write(entity)
    elif self.parse_state == ParseState.HEADING or self.parse_state == ParseState.FIRST_PAGE or self.parse_state == ParseState.NEXT_PAGE:
      self.add_current_page(entity, 0)

  def handle_comment(self, data):
    print("Encountered comment :", data)

  def handle_decl(self, decl):
    print("Encountered decl :", decl)

  def handle_pi(self, data):
    print("Encountered pi :", data)

  def unknown_decl(self, data):
    print("Encountered unknown_decl :", data)


parser = MyHTMLParser()

input_line = str()
# ignore initial new lines
for input_line in input_file:
  if input_line.startswith(u'\ufeff'):
    input_line = input_line[1:]
  if input_line == "\n":
    continue
  break

parser.feed(input_line)

for input_line in input_file:
  parser.feed(input_line)

output_file.write("\n")

input_file.close()
output_file.close()
