# python3

import argparse
import re

parser = argparse.ArgumentParser(description = "This program converts a normal book txt file into paginated twee file.")
parser.add_argument("input-file", help = "Input '.txt' file", type = argparse.FileType(mode = 'r', encoding = 'utf-8'))
parser.add_argument("output-file", help = "Output '.twee' file", type = argparse.FileType(mode = 'w', encoding = 'utf-8-sig'))
parser.add_argument("-wc", "--word-count", nargs = "?", help = "Number of words per page (default: %(default)s).", type = int, default = 300)
parser.add_argument("-mwl", "--min-words-last-page",  nargs = "?", help = "Minimum number of words on the last page of a chapter (default: %(default)s).",
                    type = int, default = 100)

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

input_line = str()

# ignore initial new lines
for input_line in input_file:
  if input_line.startswith(u'\ufeff'):
    input_line = input_line[1:]
  if input_line == "\n":
    continue
  break
output_file.writelines([input_line])

# read everything before the first Chapter
for input_line in input_file:
  if input_line.startswith("<strong>Chapter"):
    break
  output_file.writelines([input_line])

# read chapters
major_number = int(0)
minor_number = int(0)
prev_label = str("Start")
next_label = str()
end_of_file = False
while not end_of_file:
  major_number += 1
  minor_number = 0
  current_label = str(major_number) + "." + str(minor_number)
  chapter_header = [
    '<p style="text-align:left;">[[<<<|' + prev_label + ']]<span style="float:right;">[[>>>|' + current_label + ']]</span></p><br /><br />\n',
    '\n', '\n', '\n', '\n',
    ":: " + current_label + "\n",
    input_line
  ]
  output_file.writelines(chapter_header)
  if major_number == 1:
    prev_label = str("Summary")

  # get all chapter lines and count words in chapter
  chapter_lines = []
  chapter_line_word_count = []
  chapter_word_count = int(0)
  for input_line in input_file:
    if input_line.startswith("<strong>Chapter"):
      break
    line_word_count = int(0)
    if input_line != "\n":
      words = re.findall(r'\S+', input_line)
      line_word_count = len(words)
      chapter_word_count += line_word_count
    chapter_lines.append(input_line)
    chapter_line_word_count.append(line_word_count)
  else:
    end_of_file = True

  # print("Chapter total word count = %d" % chapter_word_count)
  chapter_words_used = int(0)

  line_item = int(0)
  while True:
    page_words = int(0)

    # add all lines until page_words exceed word_count per page
    while line_item < len(chapter_lines) and page_words < args.word_count:
      output_file.writelines([chapter_lines[line_item]])
      page_words += chapter_line_word_count[line_item]
      line_item += 1

    # add the rest non-empty lines
    while line_item < len(chapter_lines) and chapter_lines[line_item] != "\n":
      output_file.writelines([chapter_lines[line_item]])
      page_words += chapter_line_word_count[line_item]
      line_item += 1

    # add the rest empty lines
    while line_item < len(chapter_lines) and chapter_lines[line_item] == "\n":
      output_file.writelines([chapter_lines[line_item]])
      page_words += chapter_line_word_count[line_item]
      line_item += 1

    chapter_words_used += page_words

    # place footer
    if chapter_word_count - chapter_words_used < args.min_words_last_page:
      while line_item < len(chapter_lines):
        output_file.writelines([chapter_lines[line_item]])
        page_words += chapter_line_word_count[line_item]
        line_item += 1
      # print("Page " + current_label + " has " + str(page_words) + " words.")
      break
    else:
      # print("Page " + current_label + " has " + str(page_words) + " words.")
      minor_number += 1
      next_label = str(major_number) + "." + str(minor_number)
      page_footer = [
        '<p style="text-align:left;">[[<<<|' + prev_label + ']]<span style="float:right;">[[>>>|' + next_label + ']]</span></p><br /><br />\n',
        '\n', '\n', '\n', '\n',
        ":: " + next_label + "\n"
      ]
      output_file.writelines(page_footer)
      prev_label = current_label
      current_label = next_label

  # at the end
  prev_label = current_label

# output end of book footer
chapter_footer = [
  '<p style="text-align:left;">[[<<<|' + prev_label + ']]<span style="float:right;">[[>>>|EndShare]]</span></p><br /><br />\n',
  '\n', '\n', '\n', '\n'
]
output_file.writelines(chapter_footer)

input_file.close()
output_file.close()
