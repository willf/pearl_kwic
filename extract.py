# /// script
# dependencies = [
#   "uniseg",
# ]
# ///

import xml.etree.ElementTree as ET
import csv
from uniseg import wordbreak


def contains_alphabetic(text):
    """
    Check if the text contains any alphabetic characters.

    Args:
        text (str): The text to check.
    Returns:
        bool: True if the text contains alphabetic characters, False otherwise.
    """
    return any(char.isalpha() for char in text)


def split_on_words(text):
    """
    For each word in the line, return a list of tuples containing
    the left context, the word, and the right context.
    """
    words = list(wordbreak.words(text))
    for i, word in enumerate(words):
        left_context = "".join(words[:i])
        right_context = "".join(words[i + 1 :])
        if contains_alphabetic(word):
            yield ((left_context, word, right_context))


def create_search_link(word):
    """
    Create a search link for the word.

    Args:
        word (str): The word to create a search link for.
    Returns:
        str: The search link.
    """
    return f"https://quod.lib.umich.edu/m/middle-english-dictionary/dictionary?utf8=%E2%9C%93&search_field=hnf&q={word}"


def create_word_reference(word):
    """
    Create a markdown link for the word.

    Args:
        word (str): The word to create a markdown link for.
    Returns:
        str: The markdown link.
    """
    return f"[{word}]({create_search_link(word)})"


def extract_text(line_element):
    """
     Extract the top level text from the line element.

     for example: if the line is:
      <l><space rend="indent1"/>Of that precios perle wythouten spotte.</l>

    The extracted text would be:
    "Of that precios perle wythouten spotte."

    If the line is:
    <l><space rend="indent1"/>In <date>Augoste</date> in a hygh seysoun<note
               type="enote-indicator" n="21">N</note>
             <note type="gloss-indicator" n="46">G</note><space rend="indent2"/><gloss n="46"
               >festival</gloss></l>
     The extracted text would be:
     "In Augoste in a hygh seysoun festival"

     Keep text from text, persName, placeName, foreign, and date tags, the rest are ignored.
     The text is stripped of leading and trailing whitespace.
     Args:
         line (Element): The XML element representing the line.
     Returns:
         str: The extracted text.

    """
    keep_tags = [
        "{http://www.tei-c.org/ns/1.0}persName",
        "{http://www.tei-c.org/ns/1.0}placeName",
        "{http://www.tei-c.org/ns/1.0}foreign",
        "{http://www.tei-c.org/ns/1.0}date",
        "{http://www.tei-c.org/ns/1.0}l",
    ]
    text_parts = []

    # Add the initial text of the <l> element itself, if any
    if line_element.text:
        text_parts.append(line_element.text.strip())

    # Iterate through all child elements of the <l> tag
    for child in line_element:
        # Check if the tag is one of the allowed types
        if child.tag in keep_tags:
            if child.text:
                text_parts.append(child.text.strip())
        # Add the tail text of the child element (text following the child)
        if child.tail:
            text_parts.append(child.tail.strip())

    # Join the parts and clean up multiple spaces
    return " ".join(filter(None, text_parts))


def return_tags(line):
    """
    Return the tags in the line element.

    Args:
        line (Element): The XML element representing the line.
    Returns:
        list: A list of tags in the line.
    """
    return [tag.tag for tag in line]


def return_tags_with_text(line):
    """
    Return the tags and their text in the line element.

    Args:
        line (Element): The XML element representing the line.
    Returns:
        list: A list of tuples containing the tag and its text.
    """
    return [(tag.tag, tag.text) for tag in line]


def extract_texts(xml_file):
    """
    Extracts the text from each <l> element in the XML file.

    Args:
        xml_file (str): Path to the input XML file.
    Returns:
        list: A list of extracted texts.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define the TEI namespace
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}

    # Extract texts
    for line in root.findall(".//tei:l", ns):
        text = extract_text(line)
        print(text)


def create_line_reference(line_number):
    """
    Create a line reference for the given line number.

    Args:
        line_number (int): The line number to create a reference for.
    Returns:
        str: The line reference.
    """
    return f"[Pearl](https://metseditions.org/editions/RZ5r80ETbe1cKVpHvm1RUl9eMrNR8l): {line_number}"


def extract_all_tags(xml_file):
    """
    Extracts all tags from from each <l> element in the XML file.

    Args:
        xml_file (str): Path to the input XML file.
    Returns:
        list: A list of all tags in the XML file.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define the TEI namespace
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}

    # Extract all tags
    for line in root.findall(".//tei:l", ns):
        tags = return_tags(line)
        for tag in tags:
            print(tag)


def extract_kwic(xml_file):
    """
    Extracts the KWIC (Key Word In Context) from the XML file.

    Args:
        xml_file (str): Path to the input XML file.

    Returns:
        list: A list of tuples containing the context and the word.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    writer = csv.writer(open("kwic.csv", "w", newline=""))
    # write the csv header to standard output
    writer.writerow(
        [
            "line_number",
            "reference",
            "left_context",
            "word",
            "right_context",
            "word_reference",
            "word_lower",
        ]
    )

    # Define the TEI namespace
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}

    # Extract KWIC from each line
    for line_number, line in enumerate(root.findall(".//tei:l", ns)):
        text = extract_text(line)
        # remove newlines and tabs
        text = text.replace("\n", " ").replace("\t", " ")
        # remove multiple spaces
        text = " ".join(text.split())
        # remove leading and trailing spaces
        text = text.strip()
        for left, word, right in split_on_words(text):
            # write the csv line to standard output
            writer.writerow(
                [
                    line_number,
                    create_line_reference(line_number),
                    left,
                    word,
                    right,
                    create_word_reference(word),
                    word.lower(),
                ]
            )


if __name__ == "__main__":
    xml_file = "../stanbury-pearl/Stanbury-Pearl-Export-04-Pearl-Verse-20250430.xml"
    csv_file = "entities.csv"
    # extract_entities(xml_file, csv_file)
    extract_kwic(xml_file)
    # print(f"Entities extracted and saved to {csv_file}")
