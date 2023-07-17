import sys
# from src.logger import logging

def error_message_detail(error):
    _, _, exc_tb = sys.exc_info() # error detail
    fname = exc_tb.tb_frame.f_code.co_filename
    lnum = exc_tb.tb_lineno
    error_message = (
        f"Error occured in python script name [{fname}] line number [{lnum}] error message [{str(error)}]")

    return error_message

class CustomException(Exception):
    def __init__(self, error_message):
        super().__init__(error_message)
        self.error_message = error_message_detail(error=error_message)

    def __str__(self):
        return self.error_message