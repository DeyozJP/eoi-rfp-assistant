import logging 
import os

def setup_logger(name=__name__, log_file="logs/app.log", level=logging.INFO):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


        # File handler 
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


        # Console handler 
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Logger setup 
        logger = logging.getLogger(name)
        logger.setLevel(level)
    
        logger.addHandler(console_handler)

        # Avoid duplicate logs
        logger.popagate = False

    return logger