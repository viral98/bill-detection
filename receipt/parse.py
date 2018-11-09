import time
import re
from os import listdir
from os.path import isfile, join
from difflib import get_close_matches
from collections import defaultdict
import yaml


class Receipt(object):
    def __init__(self, config, raw):
        self.config = config
        self.date = self.sum = None
        self.raw = self.normalize(raw)
        self.parse()

    def normalize(self, raw):
        normalized_lines = []
        for line in raw:
            norm_line = line.strip()
            if not norm_line:
                continue
            else:    
                norm_line = norm_line.lower()
                norm_line = norm_line.replace(",","")
                norm_line = norm_line.replace("subtotal","")
                normalized_lines.append(norm_line)
        return normalized_lines

    def parse(self):
        self.date = self.parse_date()
        self.sum = self.parse_sum()
        self.tax = self.parse_tax()

    def find(self, keyword, accuracy=0.6):
        for line in self.raw:
            words = line.split()
            matches = get_close_matches(keyword, words, 1, accuracy)
            if matches:
                return line

    def parse_date(self):
        for line in self.raw:
            m = re.search(self.config.date_format, line)
            if m:
                return m.group(0)

    
    def parse_sum(self):
        for sum_key in self.config.sum_keys:
            sum_line = self.find(sum_key)
            if sum_line:
                sum_float = re.search(self.config.sum_format, sum_line)
                if sum_float:
                    return sum_float.group(0)

    def parse_tax(self):
        for tax_key in self.config.tax_keys:
            tax_line = self.find(tax_key)
            if tax_line:
                tax_float = re.search(self.config.tax_format, tax_line)
                if tax_float:
                    return tax_float.group(0)

class objectview(object):
    def __init__(self, d):
        self.__dict__ = d

def parse():
    config = read_config()
    receipt_files = [f for f in listdir(config.receipts_path)
                     if isfile(join(config.receipts_path, f))]
    receipt_files = [f for f in receipt_files if not f.startswith('.')]
    stats = defaultdict(int)

    for receipt_file in receipt_files:
        receipt_path = join(config.receipts_path, receipt_file)
        with open(receipt_path) as receipt:
            lines = receipt.readlines()
            receipt = Receipt(config, lines)
            result=[]
            r1 = receipt.date
            r2 = receipt.sum
            r3 = receipt.tax
            result.append(r1)
            result.append(r2)
            result.append(r3)
            return result
        
def read_config():
    stream = open("receipt/config.yml", "r")
    docs = yaml.safe_load(stream)
    return objectview(docs)
parse()