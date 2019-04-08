# To run this code, first edit config.py with your configuration
#

#!/usr/bin/python3
#-*- coding: utf-8 -*-
import time
import re
import urllib.parse
import urllib.request

import config
import sqliteOperations


class PipelineCaller(object):

    DEFAULT_SENTENCE_SPLIT_DELIMITER_CLASS = '[\.\?:;!]'

    def __init__(self, tool='normalize', text='example', token=config.ITU_NLP_API_TOKEN, processing_type='sentence'):
        self.tool = tool
        self.text = text
        self.token = token
        self.processing_type = processing_type

        self.sentences = []
        self.words = []

    def call(self):

        if self.processing_type == 'whole':
            params = self.encode_parameters(self.text)
            return self.request(params)

        if self.processing_type == 'sentence':
            results = []
            self.parse_sentences()

            for sentence in self.sentences:
                params = self.encode_parameters(sentence)
                results.append(self.request(params))

            return "\n".join(results)

        if self.processing_type == 'word':
            results = []
            self.parse_words()

            for word in self.words:
                params = self.encode_parameters(word)
                results.append(self.request(params))

            return "\n".join(results)

    def parse_sentences(self):
        r = re.compile(r'(?<=(?:{}))\s+'.format(PipelineCaller.DEFAULT_SENTENCE_SPLIT_DELIMITER_CLASS))
        self.sentences = r.split(self.text)

        if re.match('^\s*$', self.sentences[-1]):
            self.sentences.pop(-1)

    def parse_words(self):
        self.parse_sentences()

        for sentence in self.sentences:
            for word in sentence.split():
                self.words.append(word)

    def encode_parameters(self, text):
        return urllib.parse.urlencode({'tool': self.tool, 'input': text, 'token': self.token}).encode(config.PIPELINE_ENCODING)
    
    def request(self, params):
        response = urllib.request.urlopen(config.API_URL, params)
        return response.read().decode(config.PIPELINE_ENCODING)

def main():
    # create a database connection
    conn = sqliteOperations.createConnection(sqliteOperations.database)
    with conn:
        rows = sqliteOperations.selectTaskByStatus(conn,"0")
        for row in rows:
            findInRow(row)

    sqliteOperations.UpdateTaskByStatus(conn,"1")
    
    with open(config.STEP_3_INPUT_DIR, encoding=config.PIPELINE_ENCODING) as input_file:
        text = input_file.read()
    
    config.logger.info(text)
    config.logger.info(config.ITU_NLP_API_TOKEN)
    config.logger.info(config.STEP_4_INPUT_DIR)
    config.logger.info(config.API_URL)
    config.logger.info(config.PIPELINE_ENCODING)
    config.logger.info(config.STEP_3_INPUT_DIR)
    config.logger.info(config.DEFAULT_TOOL)

    REQUEST_URL = config.API_URL + "?" + "tool=" + config.DEFAULT_TOOL + "&input=" + "MERHABAAAAAA" + "&token=" + config.ITU_NLP_API_TOKEN
    config.logger.info(REQUEST_URL)

    start_time = time.time()

    caller = PipelineCaller(config.DEFAULT_TOOL, text, config.ITU_NLP_API_TOKEN, 'sentence')
    with open(config.STEP_4_INPUT_DIR, 'w', encoding = config.PIPELINE_ENCODING) as output_file:
        output_file.write('{}\n'.format(caller.call()))

    process_time = time.time() - start_time

    config.logger.info("[DONE] It took {0:.0f} seconds to process whole text.".format(process_time))

if __name__ == '__main__':
	main()