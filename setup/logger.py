import logging

logging.basicConfig(filename='report.log', encoding='utf-8',
                    format='%(asctime)s | MT-REPORT | %(levelname)s | %(message)s', 
                    level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

def loginfo(message):
    return logging.info(f'{message}')

def logerror(message):
    return logging.error(f'{message}')